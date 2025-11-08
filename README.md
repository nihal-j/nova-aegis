# 🛡️ Aegis — Test before you trust

**Premium Safety Guardrails for Code Changes**

---

## 👋 New User? Start Here!

**Welcome!** Aegis is a safety system that validates code changes before they're applied. Think of it as a "seatbelt for AI helpers" that checks policies, runs tests in a sandbox, and generates risk assessments.

### 🎯 Quick Onboarding (5 minutes)

1. **Read this first** → Understand what Aegis does (you're here!)
2. **Run the app** → `bash scripts/dev.sh` (see Quickstart below)
3. **Try the demo** → Open http://127.0.0.1:8501 and click "Run with Aegis"
4. **Read the docs** → Click "📖 Architecture" in the UI header for deep dive

### 📚 Learning Path

**For complete beginners:**
1. ✅ **ONBOARDING.md** - Complete step-by-step guide (start here!)
2. ✅ **README.md** (this file) - Quick reference and features
3. ✅ **UI Welcome Panel** - Interactive intro when you first open the app
4. ✅ **60-Second Demo** (below) - Try unsafe vs safe actions
5. ✅ **docs/WALKTHROUGH.md** - Hands-on tutorial with examples
6. ✅ **docs/ARCHITECTURE.md** - How it works under the hood

**For developers:**
- Start with **docs/ARCHITECTURE.md** for system design
- Check **docs/WALKTHROUGH.md** for code examples
- Explore `app/` modules (all have docstrings)

### 🚀 What Aegis Does

Aegis validates code changes through this flow:
```
Policy Check → Sandbox Copy → Apply Changes → Run Tests → Risk Assessment
```

If any step fails → **BLOCKED** ❌  
If all pass → **ALLOWED** ✅

---

## 🚀 5-Minute Quickstart

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd nova-aegis
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development servers:**
   ```bash
   bash scripts/dev.sh
   ```

   This will start:
   - **Backend API** at http://127.0.0.1:8000
   - **Streamlit UI** at http://127.0.0.1:8501
   - **API Documentation** at http://127.0.0.1:8000/docs

5. **Open your browser:**
   Navigate to http://127.0.0.1:8501 to use the Aegis UI.

That's it! Aegis is ready to use. No API keys required for basic functionality.

---

## 🎯 60-Second Demo

### Step 1: Test an Unsafe Action (Should Block)
1. In the UI, select **"Unsafe delete"** preset
2. Click **"Run with Aegis"**
3. **Result:** Action is **BLOCKED** ❌
   - Policy check fails (destructive intent detected)
   - Risk score is high
   - Explanation shows why it was blocked

### Step 2: Test a Safe Action (Should Allow)
1. Select **"Safe pagination"** preset
2. Click **"Run with Aegis"**
3. **Result:** Action is **ALLOWED** ✅
   - All checks pass
   - Tests run successfully
   - Low risk score

### Step 3: Toggle Modal Cloud Sandbox
1. Check **"Use Modal cloud sandbox"**
2. Run an action
3. **Note:** Requires `DEMO_REPO` in `.env` and Modal token configured
   - If not configured, falls back to local sandbox gracefully

### Step 4: View HTML Report
1. After running an action, click **"View HTML Report"** link
2. See a formatted HTML report with all details
3. Or visit http://127.0.0.1:8000/riskcard/html directly

---

## 📋 Features

### Core Features
- ✅ **Policy Checks** - Validate file paths, intents, and content structure
- ✅ **Sandbox Testing** - Run pytest in isolated environment (local or Modal cloud)
- ✅ **Risk Scoring** - 0-100 risk score with LOW/MEDIUM/HIGH/CRITICAL levels
- ✅ **AI Explanations** - Claude-powered explanations (optional, falls back to plain text)
- ✅ **Diff Analysis** - Detect risky patterns (DELETE, DROP, secrets, etc.)

### Advanced Features
- 📜 **History & Audit Log** - SQLite database of all risk assessments
- ✅ **Approval Workflow** - Override blocked actions with approval
- 📊 **Performance Metrics** - Track API performance and errors
- 🔗 **Webhook Integration** - Send notifications to external services
- 🎨 **Premium Dark UI** - Beautiful, beginner-friendly interface

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Optional: GitHub repo URL for Modal cloud sandbox
DEMO_REPO=https://github.com/your-org/your-repo.git

# Optional: Webhook URL for notifications
AEGIS_WEBHOOK_URL=https://your-webhook-url.com
```

### OpenRouter API Key (Optional)

For AI-powered explanations:
1. Create `OPENROUTER_API_KEY.txt` in the project root
2. Add your OpenRouter API key (one line)
3. If not provided, Aegis uses plain-English explanations

---

## 🐛 Troubleshooting

### 404 at "/" endpoint
**Problem:** Getting 404 when accessing root endpoint.

**Solution:** This is normal! The root endpoint (`/`) returns JSON with API links. Use:
- UI: http://127.0.0.1:8501
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### Modal DEMO_REPO Error
**Problem:** "DEMO_REPO not configured" when using Modal.

**Solution:**
1. Add `DEMO_REPO=https://github.com/your-org/your-repo.git` to `.env`
2. Configure Modal token: `modal token set`
3. If Modal fails, Aegis automatically falls back to local sandbox

### Backend URL Connection Error
**Problem:** UI shows "Backend down" or connection errors.

**Solution:**
1. Ensure backend is running: `uvicorn app.app:app --reload`
2. Check backend URL in UI sidebar (default: http://127.0.0.1:8000)
3. Verify no firewall blocking port 8000
4. Check backend logs for errors

### Port Already in Use
**Problem:** "Address already in use" error.

**Solution:**
```bash
# Kill processes on ports 8000 and 8501
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

### Import Errors
**Problem:** ModuleNotFoundError when running.

**Solution:**
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check you're in the project root directory

---

## 📚 API Endpoints

### Core Endpoints
- `GET /` - API information and links
- `GET /health` - Health check
- `GET /riskcard` - Get latest risk card
- `GET /riskcard/html` - HTML report
- `POST /propose_action` - Submit action for risk assessment

### Advanced Endpoints
- `GET /riskcard/history` - Get risk card history
- `GET /riskcard/{request_id}` - Get specific risk card
- `POST /riskcard/{request_id}/approve` - Approve blocked action
- `GET /metrics` - Performance metrics

See http://127.0.0.1:8000/docs for interactive API documentation.

---

## 🏗️ Architecture

```
nova-aegis/
├── app/
│   ├── app.py              # FastAPI main application
│   ├── guards.py           # Policy checks
│   ├── dryrun_local.py     # Local sandbox
│   ├── modal_runner.py     # Modal cloud sandbox
│   ├── explain.py          # AI explanations
│   ├── history.py          # Audit log system
│   ├── risk_scoring.py     # Risk calculation
│   ├── diff_analysis.py    # Diff pattern detection
│   ├── metrics.py          # Performance tracking
│   └── webhooks.py         # Webhook integration
├── ui/
│   └── ui.py               # Streamlit frontend
├── scripts/
│   └── dev.sh              # Development launcher
└── demo/                   # Demo repository for testing
```

---

## 🎨 UI Features

### Action Builder (Left Panel)
- File selection
- Preset actions (Unsafe/Safe examples)
- Modal cloud sandbox toggle
- Real-time code preview

### Risk Card (Right Panel)
- Status badge (SAFE/BLOCKED)
- Risk score with level indicator
- PASS/FAIL check table
- AI explanation
- Risk pattern warnings
- Unified diff (copyable)
- Collapsible test output (last 80 lines)
- HTML report link
- Approval button for blocked actions
- Recent history

---

## 🔒 Safety Features

1. **Policy Enforcement**
   - File path allowlisting
   - Destructive intent blocking
   - Type and range validation

2. **Sandbox Isolation**
   - Temporary directories
   - Isolated test execution
   - Automatic cleanup

3. **Risk Detection**
   - Pattern matching (DELETE, DROP, etc.)
   - Sensitive data detection
   - Change magnitude analysis

4. **Audit Trail**
   - Complete history in SQLite
   - Request IDs for tracking
   - Approval records

---

## 🚦 Running Without Keys

Aegis works completely offline with zero API keys:
- ✅ Policy checks work
- ✅ Local sandbox works
- ✅ Risk scoring works
- ✅ Plain-English explanations work
- ✅ All UI features work

Optional enhancements (require keys):
- OpenRouter API key → AI explanations
- Modal token → Cloud sandbox
- Webhook URL → Notifications

---

## 📝 License

This project is provided as-is for demonstration purposes.

---

## 🤝 Contributing

Contributions welcome! Please ensure:
- All tests pass
- Code follows existing style
- New features include error handling
- Documentation is updated

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API docs at `/docs`
3. Check backend logs for errors

---

**🛡️ Test before you trust. Stay safe!**

