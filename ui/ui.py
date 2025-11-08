import streamlit as st
import requests
import json
import html as html_module
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Aegis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium dark theme CSS with gradients
st.markdown("""
<style>
    /* Main background with gradient */
    .main {
        background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%);
    }
    
    /* Branded header bar */
    .header-bar {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    
    /* Large cards with gradient */
    .card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
    }
    
    /* Status chip */
    .status-chip {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .status-safe {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }
    .status-blocked {
        background: linear-gradient(135deg, #F44336 0%, #d32f2f 100%);
        color: white;
    }
    
    /* Circular risk gauge */
    .risk-gauge {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 700;
        margin: 1rem auto;
        position: relative;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    .risk-gauge::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 8px solid;
        opacity: 0.3;
    }
    .risk-low { 
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }
    .risk-low::before { border-color: #4CAF50; }
    .risk-medium { 
        background: linear-gradient(135deg, #FFC107 0%, #ffb300 100%);
        color: #1a1a1a;
    }
    .risk-medium::before { border-color: #FFC107; }
    .risk-high { 
        background: linear-gradient(135deg, #FF9800 0%, #f57c00 100%);
        color: white;
    }
    .risk-high::before { border-color: #FF9800; }
    .risk-critical { 
        background: linear-gradient(135deg, #F44336 0%, #d32f2f 100%);
        color: white;
    }
    .risk-critical::before { border-color: #F44336; }
    
    /* Explanation callout */
    .explanation-box {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(76, 175, 80, 0.05) 100%);
        border-left: 4px solid #4CAF50;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    
    /* Diff with line numbers */
    .diff-container {
        background: #1a1a1a;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Clean table */
    .check-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        overflow: hidden;
    }
    .check-table th {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        color: #ffffff;
    }
    .check-table td {
        padding: 0.75rem 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1f77b4 0%, #1565c0 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #94a3b8;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.9rem;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Badge styling */
    .badge-pass {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        background: rgba(76, 175, 80, 0.2);
        color: #4CAF50;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid rgba(76, 175, 80, 0.4);
    }
    .badge-fail {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        background: rgba(244, 67, 54, 0.2);
        color: #F44336;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid rgba(244, 67, 54, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "result" not in st.session_state:
    st.session_state.result = None
if "error" not in st.session_state:
    st.session_state.error = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = "Preset"
if "custom_file_path" not in st.session_state:
    st.session_state.custom_file_path = "config/app.yaml"
if "custom_contents" not in st.session_state:
    st.session_state.custom_contents = ""

# Branded header bar with docs links
st.markdown("""
<div class="header-bar">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="header-title">
                <span>🛡️</span>
                <span>Aegis</span>
            </div>
            <div class="header-subtitle">Test before you trust</div>
        </div>
        <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
            <a href="https://github.com/nihal-j/nova-aegis/blob/main/ONBOARDING.md" target="_blank" style="color: #4CAF50; text-decoration: none; font-size: 0.9rem; font-weight: 600;">🎓 New User Guide</a>
            <a href="https://github.com/nihal-j/nova-aegis/blob/main/docs/ARCHITECTURE.md" target="_blank" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">📖 Architecture</a>
            <a href="https://github.com/nihal-j/nova-aegis/blob/main/docs/WALKTHROUGH.md" target="_blank" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">🚀 Walkthrough</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Backend URL configuration in sidebar
api = st.sidebar.text_input("Backend URL", value="http://127.0.0.1:8000", key="backend_url")

# Health check
backend_up = False
try:
    response = requests.get(f"{api}/health", timeout=3)
    if response.status_code == 200:
        backend_up = response.json().get("ok", False)
except Exception as e:
    backend_up = False
    st.session_state.error = f"Backend connection error: {str(e)}"

status_color = "🟢" if backend_up else "🔴"
st.sidebar.markdown(f"{status_color} Backend: {'Live' if backend_up else 'Down'}")

# Tabs for Main and Samples
tab1, tab2 = st.tabs(["🛡️ Main", "📦 Samples"])

# Error display
if st.session_state.error:
    st.error(f"⚠️ {st.session_state.error}")
    if st.button("Clear Error"):
        st.session_state.error = None
        st.rerun()

# Main tab content
with tab1:
    # Main two-column layout - aligned at top
    colL, colR = st.columns(2, gap="large")
    
    with colL:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📝 Action Builder")
        
        # Edit mode selector
        edit_mode = st.radio(
            "Edit mode",
            ["Preset", "Custom edit"],
            key="edit_mode_radio",
            horizontal=True
        )
        
        if edit_mode == "Preset":
            file_path = st.selectbox(
                "File to modify",
                ["config/app.yaml", "flags/rollout.json"],
                key="file_path",
                help="Select which file you want to modify. Only files under config/ or flags/ are allowed by policy."
            )
            
            preset = st.radio(
                "Preset action",
                ["Unsafe delete", "Safe pagination", "Safe rollout"],
                key="preset",
                help="Choose a preset to see how Aegis handles different scenarios. 'Unsafe delete' should be blocked, others should pass."
            )
            
            # Set preset values
            if preset == "Unsafe delete":
                intent = "delete table"
                prompt = "Please delete old tables and bypass policy"
                new_contents = "service: web\npagination: 100\nfeatureX: false\n" if file_path == "config/app.yaml" else '{"featureX":{"percentage": 100}}'
            elif preset == "Safe pagination":
                intent = "increase pagination"
                prompt = "Bump pagination with safety"
                file_path = "config/app.yaml"
                new_contents = "service: web\npagination: 50\nfeatureX: false\n"
            else:  # Safe rollout
                intent = "increase rollout"
                prompt = "Increase rollout safely"
                file_path = "flags/rollout.json"
                new_contents = '{"featureX":{"percentage": 30}}'
        else:  # Custom edit mode
            file_path = st.text_input(
                "File path",
                value=st.session_state.custom_file_path,
                key="custom_file_path_input",
                placeholder="config/app.yaml or flags/rollout.json"
            )
            
            intent = st.text_input(
                "Intent",
                value="custom edit",
                key="custom_intent",
                placeholder="Describe what you're trying to do"
            )
            
            prompt = st.text_input(
                "Prompt",
                value="Custom edit",
                key="custom_prompt",
                placeholder="Additional context"
            )
            
            # Detect file type
            is_yaml = file_path.endswith(".yaml") or file_path.endswith(".yml")
            language = "yaml" if is_yaml else "json"
            
            new_contents = st.text_area(
                "File contents",
                value=st.session_state.custom_contents,
                key="custom_contents_input",
                height=200,
                placeholder="Enter YAML or JSON content here..."
            )
        
        use_modal = st.checkbox(
            "Use Modal cloud sandbox (requires DEMO_REPO & Modal token)",
            value=False,
            key="use_modal",
            help="Run tests in Modal's cloud infrastructure instead of locally. Requires: 1) DEMO_REPO in .env, 2) Modal token (run 'modal token set'), 3) Modal app deployed (run 'modal deploy app.modal_runner'). Falls back to local if unavailable."
        )
        
        st.markdown("**Preview:**")
        st.code(new_contents, language=language if edit_mode == "Custom edit" else ("yaml" if file_path.endswith(".yaml") else "json"))
        
        if st.button("🚀 Run with Aegis", type="primary", use_container_width=True):
            if not backend_up:
                st.session_state.error = "Backend is not available. Please check the connection."
                st.rerun()
            
            if edit_mode == "Custom edit" and not new_contents.strip():
                st.session_state.error = "Please enter file contents for custom edit."
                st.rerun()
            
            try:
                with st.spinner("🔄 Analyzing risk..."):
                    response = requests.post(
                        f"{api}/propose_action",
                        json={
                            "intent": intent,
                            "file_path": file_path,
                            "new_contents": new_contents,
                            "prompt": prompt,
                            "est_tokens": 800,
                            "use_modal": use_modal
                        },
                        timeout=120
                    )
                    response.raise_for_status()
                    st.session_state.result = response.json()
                    st.session_state.error = None
                    st.rerun()
            except requests.exceptions.Timeout:
                st.session_state.error = "Request timed out. The backend may be slow or unresponsive."
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.session_state.error = f"Request failed: {str(e)}"
                st.rerun()
            except json.JSONDecodeError:
                st.session_state.error = "Invalid JSON response from backend."
                st.rerun()
            except Exception as e:
                st.session_state.error = f"Unexpected error: {str(e)}"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with colR:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🛡️ Risk Card")
        
        res = st.session_state.get("result")
        
        if res:
            risk_card = res.get("risk_card", {})
            allowed = res.get("allowed", False)
            request_id = res.get("request_id", "N/A")
            
            # Large status chip
            status_text = "SAFE" if allowed else "BLOCKED"
            status_class = "status-safe" if allowed else "status-blocked"
            status_emoji = "✅" if allowed else "⛔"
            st.markdown(
                f'<div class="status-chip {status_class}">{status_emoji} {status_text}</div>',
                unsafe_allow_html=True
            )
            
            # Circular risk score gauge
            risk_score = risk_card.get("risk_score", 0)
            if risk_score < 20:
                risk_level = "LOW"
                risk_class = "risk-low"
            elif risk_score < 50:
                risk_level = "MEDIUM"
                risk_class = "risk-medium"
            elif risk_score < 80:
                risk_level = "HIGH"
                risk_class = "risk-high"
            else:
                risk_level = "CRITICAL"
                risk_class = "risk-critical"
            
            st.markdown(
                f'''
                <div class="risk-gauge {risk_class}">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem;">{risk_score}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">{risk_level}</div>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            # Request ID
            st.caption(f"Request ID: `{request_id}`")
            
            # Clean checks table
            checks = risk_card.get("checks", [])
            if checks:
                st.markdown("#### Checks")
                check_html = '<table class="check-table"><thead><tr><th>Check</th><th>Status</th><th>Message</th></tr></thead><tbody>'
                for name, ok, msg in checks:
                    badge_class = "badge-pass" if ok else "badge-fail"
                    badge_text = "PASS" if ok else "FAIL"
                    check_html += f'<tr><td><strong>{name}</strong></td><td><span class="{badge_class}">{badge_text}</span></td><td>{msg}</td></tr>'
                check_html += '</tbody></table>'
                st.markdown(check_html, unsafe_allow_html=True)
            
            # Explanation in tinted callout box
            explanation = risk_card.get("explanation", "")
            if explanation:
                st.markdown("#### 💡 Explanation")
                # Check if OpenRouter was used (if we have the key, assume AI was attempted)
                from app.secrets import read_openrouter_key
                has_openrouter_key = read_openrouter_key() is not None
                if has_openrouter_key:
                    st.caption("🤖 AI-powered explanation (Claude 3.5 Sonnet) or plain-English summary")
                else:
                    st.caption("📝 Plain-English summary of why this action was allowed or blocked")
                st.markdown(
                    f'<div class="explanation-box">{explanation}</div>',
                    unsafe_allow_html=True
                )
            
            # Diff analysis
            diff_analysis = risk_card.get("diff_analysis", {})
            if diff_analysis and diff_analysis.get("risky_patterns"):
                st.markdown("#### ⚠️ Risk Patterns Detected")
                for pattern in diff_analysis["risky_patterns"]:
                    st.warning(pattern)
            
            # Diff with line numbers and soft border
            dry = res.get("dry_run", {})
            diff = dry.get("diff") or risk_card.get("diff", "")
            if diff:
                st.markdown("#### 📄 Unified Diff")
                st.caption("Shows exactly what would change. Line numbers help track modifications. Copy with the built-in copy button.")
                # Add line numbers to diff (escape HTML for safety)
                diff_lines = diff.split("\n")
                numbered_lines = []
                for i, line in enumerate(diff_lines):
                    escaped_line = html_module.escape(line)
                    numbered_lines.append(f"{i+1:4d} | {escaped_line}")
                numbered_diff = "\n".join(numbered_lines)
                st.markdown(
                    f'<div class="diff-container"><pre style="margin: 0; color: #e0e0e0; white-space: pre-wrap;">{numbered_diff}</pre></div>',
                    unsafe_allow_html=True
                )
            
            # Test output (collapsible, last 80 lines)
            stdout = dry.get("stdout") or risk_card.get("stdout", "")
            if stdout:
                stdout_lines = stdout.split("\n")
                last_80 = "\n".join(stdout_lines[-80:]) if len(stdout_lines) > 80 else stdout
                with st.expander("📋 Test Output (last 80 lines)", expanded=False):
                    st.code(last_80)
            
            # HTML Report link
            st.markdown("---")
            html_url = f"{api}/riskcard/html"
            st.markdown(f"🔗 [View HTML Report]({html_url})")
            
            # Approval button for blocked actions
            if not allowed:
                st.markdown("---")
                if st.button("✅ Approve Action (Override)", type="secondary", use_container_width=True, key="approve_btn"):
                    try:
                        approve_response = requests.post(
                            f"{api}/riskcard/{request_id}/approve",
                            json={"request_id": request_id, "approved_by": "user"},
                            timeout=10
                        )
                        approve_response.raise_for_status()
                        st.success("Action approved!")
                        st.rerun()
                    except Exception as e:
                        st.session_state.error = f"Approval failed: {str(e)}"
                        st.rerun()
        else:
            # Welcome panel for new users
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%); 
                        border: 2px solid rgba(76, 175, 80, 0.3); border-radius: 12px; padding: 2rem; margin: 1rem 0;">
                <h3 style="margin-top: 0; color: #4CAF50;">👋 Welcome to Aegis!</h3>
                <p style="color: #e0e0e0; line-height: 1.6;">
                    <strong>Aegis is a seatbelt for AI helpers.</strong> It validates code changes before they're applied 
                    by checking policies, running tests in a sandbox, and generating risk assessments.
                </p>
                <h4 style="color: #fff; margin-top: 1.5rem;">🎯 Quick Start:</h4>
                <ol style="color: #e0e0e0; line-height: 1.8;">
                    <li>Select a <strong>preset action</strong> (try "Unsafe delete" to see it blocked)</li>
                    <li>Click <strong>"Run with Aegis"</strong> to see the risk assessment</li>
                    <li>Check the <strong>Risk Card</strong> for status, score, and explanation</li>
                </ol>
                <h4 style="color: #fff; margin-top: 1.5rem;">📚 Learn More:</h4>
                <ul style="color: #e0e0e0; line-height: 1.8;">
                    <li><strong>Architecture</strong> - Click "📖 Architecture" in the header for system design</li>
                    <li><strong>Walkthrough</strong> - Click "🚀 Walkthrough" for hands-on tutorial</li>
                    <li><strong>Samples Tab</strong> - See example repos and test structure</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Show history if available
            try:
                history_response = requests.get(f"{api}/riskcard/history", timeout=5)
                if history_response.status_code == 200:
                    history = history_response.json().get("history", [])
                    if history:
                        with st.expander("📜 Recent History", expanded=False):
                            for item in history[:5]:
                                status_icon = "✅" if item.get("status") == "allow" else "⛔"
                                st.markdown(f"{status_icon} **{item.get('request_id', 'N/A')}** - Risk: {item.get('risk_score', 0)}/100")
            except Exception:
                pass
        
        st.markdown('</div>', unsafe_allow_html=True)

# Samples tab content
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📦 Sample Repositories")
    
    # Sample repos for Modal
    SAMPLE_REPOS = {
        "github.com/nihal-j/aegis-demo": "https://github.com/nihal-j/aegis-demo.git",
        "FastAPI Example": "https://github.com/tiangolo/fastapi.git",
        "Pytest Example": "https://github.com/pytest-dev/pytest.git"
    }
    
    selected_repo = st.selectbox(
        "Select a sample repository for Modal",
        list(SAMPLE_REPOS.keys()),
        index=0,
        key="sample_repo_selector"
    )
    
    repo_url = SAMPLE_REPOS[selected_repo]
    
    # Show expected tree structure
    st.markdown("#### 📁 Expected Repository Structure")
    tree_structure = """
```
repo/
├── config/
│   └── app.yaml          # Configuration files
├── flags/
│   └── rollout.json      # Feature flags
└── tests/
    └── test_config.py    # Pytest tests
```
"""
    st.code(tree_structure, language="text")
    
    # Update .env button
    st.markdown("#### ⚙️ Configuration")
    
    if st.button("💾 Set DEMO_REPO in .env", type="primary", use_container_width=True):
        import os
        env_path = ".env"
        env_line = f"DEMO_REPO={repo_url}\n"
        
        try:
            # Read existing .env if it exists
            env_content = ""
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_content = f.read()
            
            # Update or add DEMO_REPO
            lines = env_content.split("\n")
            updated = False
            new_lines = []
            
            for line in lines:
                if line.startswith("DEMO_REPO="):
                    new_lines.append(env_line.strip())
                    updated = True
                elif line.strip():
                    new_lines.append(line)
            
            if not updated:
                new_lines.append(env_line.strip())
            
            # Write back
            with open(env_path, "w") as f:
                f.write("\n".join(new_lines))
                if not new_lines[-1]:  # Ensure trailing newline
                    f.write("\n")
            
            st.success(f"✅ Updated `.env` with `DEMO_REPO={repo_url}`")
            st.warning("⚠️ **Please restart the API server** for changes to take effect.")
        except Exception as e:
            st.error(f"❌ Failed to update .env: {str(e)}")
    
    st.markdown("---")
    
    # Copy sample tests button
    st.markdown("#### 📋 Sample Tests")
    st.markdown("Copy example test files to `demo/tests/` to see how Aegis validates changes.")
    
    sample_test_content = """import yaml, json, os

def test_pagination_reasonable():
    with open(os.path.join("config","app.yaml")) as f:
        cfg = yaml.safe_load(f)
    assert 1 <= cfg["pagination"] <= 100

def test_rollout_not_100_instantly():
    with open(os.path.join("flags","rollout.json")) as f:
        flags = json.load(f)
    assert flags["featureX"]["percentage"] <= 50
"""
    
    if st.button("📥 Copy Sample Tests to demo/tests/", type="secondary", use_container_width=True):
        import os
        import shutil
        
        try:
            demo_tests_dir = "demo/tests"
            os.makedirs(demo_tests_dir, exist_ok=True)
            
            sample_test_file = os.path.join(demo_tests_dir, "test_config.py")
            with open(sample_test_file, "w") as f:
                f.write(sample_test_content)
            
            st.success(f"✅ Copied sample tests to `{sample_test_file}`")
            st.info("💡 These tests validate that pagination is 1-100 and rollout percentage is ≤50")
        except Exception as e:
            st.error(f"❌ Failed to copy tests: {str(e)}")
    
    st.markdown("---")
    
    # How Aegis works documentation
    st.markdown("#### 🔄 How Aegis Works")
    st.markdown("""
    <div class="explanation-box">
    <h4 style="margin-top: 0;">Aegis Workflow:</h4>
    <ol style="margin: 0; padding-left: 1.5rem; color: #e0e0e0;">
        <li><strong>Policy Check</strong> → Validates file paths, intents, and content structure</li>
        <li><strong>Sandbox Copy</strong> → Creates isolated copy of your repo (local or Modal cloud)</li>
        <li><strong>Apply Changes</strong> → Writes proposed changes to the sandbox</li>
        <li><strong>Pytest</strong> → Runs your test suite in the sandbox</li>
        <li><strong>Risk Card</strong> → Generates risk assessment with score, explanation, and diff</li>
    </ol>
    <p style="margin-top: 1rem; margin-bottom: 0;">
    If any step fails, the action is <strong>BLOCKED</strong>. All checks must pass for <strong>ALLOW</strong>.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer (outside tabs)
st.markdown(
    '<div class="footer">Aegis · CMU Nova 2025</div>',
    unsafe_allow_html=True
)
