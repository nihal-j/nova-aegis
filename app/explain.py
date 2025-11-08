"""
Explanation generation for Aegis.

Generates human-readable explanations of risk assessments. Uses OpenRouter
(Claude 3.5 Sonnet) if API key is available, otherwise builds plain-English
explanations from checks and diff analysis.

Always returns a string - never crashes, even if OpenRouter fails.
"""
from app.secrets import read_openrouter_key
from app.openrouter import call_openrouter


def explain_reason(risk_card: dict, max_chars: int = 280) -> str:
    """
    Generate a concise explanation of the risk assessment.
    Uses OpenRouter if API key is available, otherwise builds a plain-English explanation.
    Never crashes; always returns a string.
    """
    try:
        # Try OpenRouter first if key is available
        api_key = read_openrouter_key()
        if api_key:
            try:
                # Build prompt for OpenRouter
                checks = risk_card.get("checks", [])
                status = risk_card.get("status", "unknown")
                diff = risk_card.get("diff", "")
                
                check_summary = "\n".join([
                    f"- {name}: {'PASS' if ok else 'FAIL'} - {msg}"
                    for name, ok, msg in checks
                ])
                
                diff_summary = ""
                if diff:
                    # Extract key changes from unified diff
                    lines = diff.split("\n")
                    added = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
                    removed = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
                    diff_summary = f"Changes: {added} lines added, {removed} lines removed."
                
                prompt = f"""Summarize this risk assessment in {max_chars} characters or less:

Status: {status}
Checks:
{check_summary}
{diff_summary}

Provide a concise, plain-English explanation of why this action was {'allowed' if status == 'allow' else 'blocked'}."""
                
                explanation = call_openrouter(prompt, api_key)
                if explanation:
                    # Truncate to max_chars if needed
                    if len(explanation) > max_chars:
                        explanation = explanation[:max_chars-3] + "..."
                    return explanation
            except Exception:
                # Fall through to local explanation if OpenRouter fails
                pass
        
        # Build local explanation from checks and diff
        checks = risk_card.get("checks", [])
        status = risk_card.get("status", "unknown")
        diff = risk_card.get("diff", "")
        
        # Summarize checks
        passed = [name for name, ok, msg in checks if ok]
        failed = [name for name, ok, msg in checks if not ok]
        
        parts = []
        if status == "allow":
            parts.append("Action is safe")
        else:
            parts.append("Action is blocked")
        
        if failed:
            parts.append(f"due to failed checks: {', '.join(failed)}")
        elif passed:
            parts.append(f"all checks passed: {', '.join(passed)}")
        
        # Add diff summary if available
        if diff:
            lines = diff.split("\n")
            added = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
            removed = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
            if added > 0 or removed > 0:
                parts.append(f"({added} added, {removed} removed)")
        
        explanation = ". ".join(parts) + "."
        
        # Truncate to max_chars if needed
        if len(explanation) > max_chars:
            explanation = explanation[:max_chars-3] + "..."
        
        return explanation
        
    except Exception:
        # Ultimate fallback - never crash
        return "Risk assessment completed."

