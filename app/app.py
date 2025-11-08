"""
Aegis FastAPI Application

Main API server that handles risk assessment requests. Coordinates policy checks,
sandbox execution, risk scoring, and explanation generation.

Flow: Policy Check → Sandbox (Local/Modal) → Pytest → Risk Scoring → Explanation → Risk Card

See docs/ARCHITECTURE.md for detailed architecture overview.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.guards import policy_check
from app.dryrun_local import dry_run as local_run
from app.explain import explain_reason

# Import Modal runner with graceful fallback
try:
    from app.modal_runner import dry_run_repo as modal_run
    MODAL_AVAILABLE = True
except Exception:
    MODAL_AVAILABLE = False
    modal_run = None
from app.history import save_risk_card, get_history, get_risk_card, approve_risk_card
from app.risk_scoring import calculate_risk_score, get_risk_level
from app.diff_analysis import analyze_diff
from app.metrics import record_request, get_metrics
from app.webhooks import send_webhook
import time, os
import html as html_module
import uuid
from dotenv import load_dotenv

# Ensure dotenv is loaded at import
load_dotenv()
DEMO_REPO = os.getenv("DEMO_REPO")

class Action(BaseModel):
    intent: str
    file_path: str
    new_contents: str
    prompt: str
    est_tokens: int = 800
    use_modal: bool = False  # toggle cloud vs local

class ApprovalRequest(BaseModel):
    request_id: str
    approved_by: str = "user"
    comment: str = ""

app = FastAPI(title="Aegis API", version="1.0.0")
LATEST = None

@app.get("/")
def root():
    """Root endpoint with API links."""
    base_url = "http://127.0.0.1:8000"
    return {
        "service": "Aegis",
        "version": "1.0.0",
        "description": "Test before you trust - Safety guardrails for code changes",
        "endpoints": {
            "health": f"{base_url}/health",
            "riskcard": f"{base_url}/riskcard",
            "riskcard_html": f"{base_url}/riskcard/html",
            "history": f"{base_url}/riskcard/history",
            "metrics": f"{base_url}/metrics",
            "docs": f"{base_url}/docs"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"ok": True, "service": "aegis", "timestamp": time.time()}

@app.get("/riskcard")
def riskcard():
    """Get the latest risk card."""
    return LATEST or {"msg": "no actions yet"}

@app.get("/riskcard/history")
def riskcard_history(limit: int = 50):
    """Get risk card history."""
    return {"history": get_history(limit)}

@app.get("/riskcard/html", response_class=HTMLResponse)
def riskcard_html():
    """Return an HTML report of the risk card."""
    if not LATEST:
        return "<html><body><p>No actions yet</p></body></html>"
    
    status = LATEST.get("status", "unknown")
    checks = LATEST.get("checks", [])
    explanation = LATEST.get("explanation", "")
    diff = LATEST.get("diff", "")
    risk_score = LATEST.get("risk_score", 0)
    risk_level, risk_color = get_risk_level(risk_score)
    
    # Status badge
    status_color = "green" if status == "allow" else "red"
    status_text = "ALLOW" if status == "allow" else "BLOCKED"
    
    # Build checks table
    checks_rows = ""
    for name, ok, msg in checks:
        badge = f'<span style="background: {"green" if ok else "red"}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">{"PASS" if ok else "FAIL"}</span>'
        checks_rows += f"<tr><td>{html_module.escape(str(name))}</td><td>{badge}</td><td>{html_module.escape(str(msg))}</td></tr>"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Aegis Risk Card</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #e0e0e0; }}
        .status-badge {{ 
            display: inline-block; 
            padding: 8px 16px; 
            border-radius: 4px; 
            color: white; 
            font-weight: bold;
            background: {status_color};
            margin: 10px 0;
        }}
        .risk-score {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            background: {risk_color};
            margin: 10px 0;
        }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background: #2a2a2a; }}
        th, td {{ border: 1px solid #444; padding: 8px; text-align: left; }}
        th {{ background-color: #333; color: #fff; }}
        pre {{ background: #2a2a2a; padding: 10px; border-radius: 4px; overflow-x: auto; color: #e0e0e0; border: 1px solid #444; }}
        .explanation {{ margin: 20px 0; padding: 10px; background: #2a2a2a; border-left: 4px solid #4CAF50; border-radius: 4px; }}
        h1, h2, h3 {{ color: #fff; }}
    </style>
</head>
<body>
    <h1>🛡️ Aegis Risk Card</h1>
    <div class="status-badge">{status_text}</div>
    <div class="risk-score">Risk Score: {risk_score}/100 ({risk_level})</div>
    
    <h2>Checks</h2>
    <table>
        <tr><th>Check</th><th>Status</th><th>Message</th></tr>
        {checks_rows}
    </table>
    
    {f'<div class="explanation"><h3>Explanation</h3><p>{html_module.escape(explanation)}</p></div>' if explanation else ''}
    
    {f'<h2>Unified Diff</h2><pre>{html_module.escape(diff)}</pre>' if diff else ''}
</body>
</html>"""
    
    return html

@app.get("/riskcard/{request_id}")
def riskcard_by_id(request_id: str):
    """Get a specific risk card by request_id."""
    card = get_risk_card(request_id)
    if not card:
        raise HTTPException(status_code=404, detail="Risk card not found")
    return card

@app.post("/riskcard/{request_id}/approve")
def approve_card(request_id: str, approval: ApprovalRequest):
    """Approve a blocked risk card."""
    success = approve_risk_card(request_id, approval.approved_by)
    if not success:
        raise HTTPException(status_code=404, detail="Risk card not found")
    return {"approved": True, "request_id": request_id, "approved_by": approval.approved_by}

@app.get("/metrics")
def metrics():
    """Get performance metrics."""
    return get_metrics()

@app.post("/propose_action")
def propose(a: Action):
    """Propose an action and get a risk assessment."""
    global LATEST
    start_time = time.time()
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    try:
        checks = []
        
        # Policy check - validates file paths, intents, and content structure
        ok1, msg1 = policy_check(a.dict())
        checks.append(("policy", ok1, msg1))
        
        if not all(x[1] for x in checks):
            LATEST = {
                "status": "blocked",
                "checks": checks,
                "ts": time.time(),
                "action": a.dict(),
                "request_id": request_id
            }
            LATEST["risk_score"] = calculate_risk_score(LATEST)
            LATEST["explanation"] = explain_reason(LATEST)
            LATEST["diff_analysis"] = analyze_diff("")
            
            save_risk_card(LATEST, request_id, time.time() - start_time)
            send_webhook(LATEST)
            record_request("/propose_action", time.time() - start_time, True)
            
            return {"allowed": False, "risk_card": LATEST, "request_id": request_id}

        # Sandbox selection - choose Modal cloud or local execution
        res = None
        if a.use_modal:
            if not MODAL_AVAILABLE:
                checks.append(("modal", False, "Modal not available (install modal package)"))
            elif not DEMO_REPO:
                checks.append(("modal", False, "DEMO_REPO not configured"))
            else:
                try:
                    # Modal requires the app to be deployed first
                    # Try to call remote function
                    res = modal_run.remote(DEMO_REPO, a.file_path, a.new_contents)
                    checks.append(("modal", True, "Modal cloud sandbox executed successfully"))
                except Exception as e:
                    error_msg = str(e)[:200]
                    # Provide more helpful error message
                    if "not found" in error_msg.lower() or "deploy" in error_msg.lower():
                        checks.append(("modal", False, "Modal app not deployed. Run: modal deploy app.modal_runner"))
                    elif "token" in error_msg.lower() or "auth" in error_msg.lower():
                        checks.append(("modal", False, "Modal authentication failed. Run: modal token set"))
                    else:
                        checks.append(("modal", False, f"Modal error: {error_msg}"))
                    res = None
        
        # Fallback to local if Modal failed or not requested
        if res is None:
            res = local_run(a.file_path, a.new_contents)
        
        checks.append(("dry_run_tests", res["ok"], "pytest passed" if res["ok"] else (res.get("stderr", "")[:200] or "tests failed")))
        
        LATEST = {
            "status": "allow" if res["ok"] else "blocked",
            "checks": checks,
            "diff": res.get("diff", ""),
            "stdout": res.get("stdout", ""),
            "ts": time.time(),
            "request_id": request_id
        }
        
        # Risk assessment - calculate score, generate explanation, analyze diff patterns
        LATEST["risk_score"] = calculate_risk_score(LATEST)
        LATEST["explanation"] = explain_reason(LATEST)
        LATEST["diff_analysis"] = analyze_diff(LATEST.get("diff", ""))
        
        execution_time = time.time() - start_time
        save_risk_card(LATEST, request_id, execution_time)
        send_webhook(LATEST)
        record_request("/propose_action", execution_time, True)
        
        return {
            "allowed": res["ok"],
            "risk_card": LATEST,
            "dry_run": res,
            "request_id": request_id
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        record_request("/propose_action", execution_time, False, error_msg)
        raise HTTPException(status_code=500, detail=f"Internal error: {error_msg}")
