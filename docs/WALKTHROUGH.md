# Aegis Walkthrough

This hands-on tutorial will get you up and running with Aegis in minutes. Follow along step-by-step to see how it works.

## Step 1: Setup

### Create Virtual Environment

```bash
cd nova-aegis
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Servers

```bash
bash scripts/dev.sh
```

This starts:
- **Backend API** at http://127.0.0.1:8000
- **Streamlit UI** at http://127.0.0.1:8501
- **API Docs** at http://127.0.0.1:8000/docs

**To stop**: Press `Ctrl+C` in the terminal.

## Step 2: Test the API with curl

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"ok": true, "service": "aegis", "timestamp": 1704067200.0}
```

### Unsafe Action (Should Block)

```bash
curl -X POST http://127.0.0.1:8000/propose_action \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "delete table",
    "file_path": "config/app.yaml",
    "new_contents": "service: web\npagination: 100\nfeatureX: false\n",
    "prompt": "Please delete old tables",
    "est_tokens": 800,
    "use_modal": false
  }'
```

**What to look for:**
- `"allowed": false`
- `"status": "blocked"` in risk_card
- `"checks": [["policy", false, "Destructive intent blocked"]]`
- `"risk_score"` is high (70+)

### Safe Action (Should Allow)

```bash
curl -X POST http://127.0.0.1:8000/propose_action \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "increase pagination",
    "file_path": "config/app.yaml",
    "new_contents": "service: web\npagination: 50\nfeatureX: false\n",
    "prompt": "Bump pagination safely",
    "est_tokens": 800,
    "use_modal": false
  }'
```

**What to look for:**
- `"allowed": true`
- `"status": "allow"` in risk_card
- `"checks": [["policy", true, "OK"], ["dry_run_tests", true, "pytest passed"]]`
- `"risk_score"` is low (10-20)
- `"diff"` shows the unified diff

### Reading the Response

A successful response has this structure:

```json
{
  "allowed": true,
  "request_id": "req_abc123def456",
  "risk_card": {
    "status": "allow",
    "checks": [...],
    "risk_score": 10,
    "explanation": "...",
    "diff": "...",
    "stdout": "...",
    "ts": 1704067200.0
  },
  "dry_run": {
    "ok": true,
    "diff": "...",
    "stdout": "...",
    "stderr": ""
  }
}
```

Key fields:
- `allowed` - Boolean, can this action proceed?
- `risk_card.status` - `"allow"` or `"blocked"`
- `risk_card.checks` - List of `[name, passed, message]` tuples
- `risk_card.risk_score` - 0-100 score
- `risk_card.explanation` - Human-readable summary
- `risk_card.diff` - Unified diff of changes

## Step 3: Using Modal Cloud Sandbox

### Setup

1. **Install Modal** (if not already installed):
   ```bash
   pip install modal
   ```

2. **Set up Modal token**:
   ```bash
   modal token set
   ```
   Follow the prompts to authenticate.

3. **Set DEMO_REPO in .env**:
   ```bash
   echo "DEMO_REPO=https://github.com/nihal-j/aegis-demo.git" >> .env
   ```

4. **Deploy the Modal app** (required before first use):
   ```bash
   modal deploy app.modal_runner
   ```
   This deploys the Modal function to the cloud. You only need to do this once.

5. **Restart the API server** (Modal config is read at startup)

### Toggle Modal in UI

1. Open http://127.0.0.1:8501
2. Check "Use Modal cloud sandbox"
3. Run an action

### Common Errors and Fixes

**Error**: `"Modal not available (install modal package)"`
- **Fix**: `pip install modal`

**Error**: `"DEMO_REPO not configured"`
- **Fix**: Add `DEMO_REPO=...` to `.env` and restart API

**Error**: `"Modal error: ..."`
- **Fix**: Check Modal token with `modal token set`
- **Fix**: Verify repo URL is accessible (public or you have access)
- **Note**: Aegis automatically falls back to local sandbox

## Step 4: Adding a New Test

Let's add a test that validates feature flags have a description field.

### Edit `demo/tests/test_config.py`

```python
import yaml, json, os

def test_pagination_reasonable():
    with open(os.path.join("config","app.yaml")) as f:
        cfg = yaml.safe_load(f)
    assert 1 <= cfg["pagination"] <= 100

def test_rollout_not_100_instantly():
    with open(os.path.join("flags","rollout.json")) as f:
        flags = json.load(f)
    assert flags["featureX"]["percentage"] <= 50

# NEW TEST: Ensure feature flags have descriptions
def test_feature_flags_have_descriptions():
    with open(os.path.join("flags","rollout.json")) as f:
        flags = json.load(f)
    for feature_name, feature_data in flags.items():
        assert "description" in feature_data, f"Feature {feature_name} missing description"
```

### Test It

1. Try to modify `flags/rollout.json` without a description:
   ```json
   {"featureX": {"percentage": 30}}
   ```

2. Run through Aegis - it should **BLOCK** because the test fails

3. Modify with description:
   ```json
   {"featureX": {"percentage": 30, "description": "New feature rollout"}}
   ```

4. Run again - it should **ALLOW**

## Step 5: Changing a Policy Rule

Let's modify the policy to allow a new file path.

### Edit `app/guards.py`

Find the `ALLOWED_PATHS` constant and add your path:

```python
ALLOWED_PATHS = ["config", "flags", "scripts"]  # Added "scripts"
```

Now files under `scripts/` can be modified.

### Add Validation for New Path

If you want to validate content in `scripts/`, add a check:

```python
def policy_check(action: dict):
    fp = action.get("file_path","")
    
    # ... existing checks ...
    
    # NEW: Validate scripts/*.sh files
    if fp.startswith("scripts/") and fp.endswith(".sh"):
        contents = action.get("new_contents", "")
        # Block dangerous commands
        if "rm -rf /" in contents or "sudo" in contents:
            return False, "Dangerous shell command blocked"
    
    return True, "OK"
```

### Test It

Try modifying a file in `scripts/` - it should now pass the policy check (if it doesn't contain dangerous commands).

## Step 6: Understanding the Flow

Let's trace through what happens when you submit an action:

1. **UI sends request** → `POST /propose_action` with action JSON
2. **API receives** → Creates request_id, starts timer
3. **Policy check** → `app/guards.py::policy_check()` validates:
   - File path in allowlist?
   - Intent safe?
   - Content structure valid?
4. **If policy fails** → Return blocked Risk Card immediately
5. **If policy passes** → Choose sandbox:
   - Modal if `use_modal=true` and configured
   - Local otherwise
6. **Sandbox execution**:
   - Copy repo to temp directory
   - Apply proposed changes
   - Run `pytest -q`
   - Generate unified diff
7. **Risk scoring** → Calculate 0-100 score from checks and diff
8. **Explanation** → Generate human-readable summary
9. **Save to history** → Store in SQLite database
10. **Return Risk Card** → JSON response with full assessment

## Step 7: "Ship It" Checklist for Judges

### Demo Steps

1. ✅ **Show UI** - Open http://127.0.0.1:8501
2. ✅ **Unsafe action** - Select "Unsafe delete", show it's BLOCKED
3. ✅ **Safe action** - Select "Safe pagination", show it's ALLOWED
4. ✅ **Risk Card** - Point out risk score, explanation, diff
5. ✅ **Toggle Modal** - Show cloud sandbox option (if configured)
6. ✅ **HTML Report** - Click "View HTML Report" link
7. ✅ **History** - Show recent risk cards in UI

### Talking Points

- **"Aegis is a seatbelt for AI helpers"** - Validates changes before they're applied
- **Multi-layered safety** - Policy checks + sandbox testing + risk scoring
- **Works offline** - No API keys required for core functionality
- **Graceful degradation** - Falls back to local if Modal fails
- **Audit trail** - Complete history in SQLite database
- **Extensible** - Easy to add new policy rules and tests

### Key Features to Highlight

1. **Policy Enforcement** - Blocks dangerous intents and invalid content
2. **Sandbox Isolation** - Tests run in isolated environment
3. **Risk Scoring** - 0-100 score with pattern detection
4. **AI Explanations** - Optional Claude-powered summaries
5. **History & Approval** - Track all decisions, override if needed

### Common Questions

**Q: What if tests are flaky?**
A: Tests should be deterministic. If they fail, the action is blocked. You can approve manually if needed.

**Q: Can I use this with my own repo?**
A: Yes! Replace `demo/` with your repo structure, or set `DEMO_REPO` for Modal.

**Q: How do I add new file types?**
A: Edit `ALLOWED_PATHS` in `app/guards.py` and add validation logic.

**Q: What about secrets?**
A: Policy blocks changes to sensitive files. Tests can also validate no secrets are exposed.

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for deep dive
- Explore the code in `app/` modules
- Try the curl examples in `scripts/curl-examples.sh`
- Customize policy rules and tests for your use case

Happy guarding! 🛡️

