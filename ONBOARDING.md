# 🎓 Aegis Onboarding Guide

**Complete guide for new users who have never seen Aegis before.**

## Step 1: Understand What Aegis Is (2 minutes)

**Aegis = Safety guardrails for code changes**

Imagine you have an AI assistant that wants to modify your code. Before you let it, Aegis:
1. ✅ Checks if the change is allowed (policy)
2. ✅ Tests it in a safe sandbox
3. ✅ Tells you if it's safe or dangerous

**Real-world analogy:** It's like a seatbelt for your codebase. You wouldn't drive without one, and you shouldn't deploy code changes without checking them first.

## Step 2: Get It Running (3 minutes)

### Prerequisites Check
- [ ] Python 3.8+ installed? Run: `python3 --version`
- [ ] Terminal/command prompt open
- [ ] You're in the `nova-aegis` directory

### Installation

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
bash scripts/dev.sh
```

**What just happened?**
- Created an isolated Python environment
- Installed all required packages
- Started two servers:
  - **Backend API** (FastAPI) on port 8000
  - **Frontend UI** (Streamlit) on port 8501

### Verify It's Working

1. **Check the terminal** - You should see:
   ```
   ✅ Aegis is running!
   📍 Local URLs:
      UI:      http://127.0.0.1:8501
      API:     http://127.0.0.1:8000
   ```

2. **Open your browser** - Go to http://127.0.0.1:8501

3. **You should see:**
   - Dark-themed UI with "Aegis" header
   - Two columns: "Action Builder" (left) and "Risk Card" (right)
   - Welcome message in the Risk Card panel

## Step 3: Your First Test (2 minutes)

### Try an Unsafe Action

1. In the UI, look at the left panel ("Action Builder")
2. Select **"Unsafe delete"** from the preset actions
3. Click **"🚀 Run with Aegis"**
4. Wait 2-3 seconds

**What you should see:**
- Right panel shows: **⛔ BLOCKED**
- Risk score is high (70+)
- Explanation says why it was blocked
- Checks table shows: `policy: FAIL - Destructive intent blocked`

**Why was it blocked?** The intent contains "delete", which the policy blocks as dangerous.

### Try a Safe Action

1. Select **"Safe pagination"** preset
2. Click **"🚀 Run with Aegis"**
3. Wait 2-3 seconds

**What you should see:**
- Right panel shows: **✅ SAFE**
- Risk score is low (10-20)
- All checks pass (policy: PASS, dry_run_tests: PASS)
- You see a diff showing what would change

**Why was it allowed?** It's a safe change (increasing pagination from 20 to 50), passes policy, and tests pass.

## Step 4: Explore the UI (5 minutes)

### Action Builder (Left Panel)
- **File to modify** - Choose which file to change
- **Preset actions** - Quick examples (hover for help)
- **Custom edit** - Switch to manual mode to type your own changes
- **Use Modal** - Toggle cloud sandbox (advanced)

### Risk Card (Right Panel)
- **Status chip** - Big green (SAFE) or red (BLOCKED) badge
- **Risk gauge** - Circular score indicator (0-100)
- **Checks table** - See what passed/failed
- **Explanation** - Why it was allowed/blocked
- **Diff** - Exact changes with line numbers
- **Test output** - Collapsible pytest results

### Header Links
- **📖 Architecture** - How Aegis works (system design)
- **🚀 Walkthrough** - Hands-on tutorial with code examples

### Samples Tab
- Click **"📦 Samples"** tab
- See example repository structures
- Learn how to configure Modal
- Copy sample tests
- Read "How Aegis Works" explanation

## Step 5: Understand the Flow (5 minutes)

Read the **"🔄 How Aegis Works"** section in the Samples tab, or check `docs/ARCHITECTURE.md`.

**The flow:**
```
1. Policy Check → Is this change allowed?
   ↓ (if yes)
2. Sandbox Copy → Create isolated test environment
   ↓
3. Apply Changes → Write proposed changes to sandbox
   ↓
4. Run Tests → Execute pytest in sandbox
   ↓
5. Risk Assessment → Calculate score, generate explanation
   ↓
6. Risk Card → Show you the result
```

**If any step fails → BLOCKED**  
**If all pass → ALLOWED**

## Step 6: Read the Documentation (10 minutes)

### For Understanding
1. **docs/ARCHITECTURE.md** - System design, components, data structures
2. **README.md** - Features, configuration, troubleshooting

### For Hands-On Learning
1. **docs/WALKTHROUGH.md** - Step-by-step examples
2. **scripts/curl-examples.sh** - API examples you can run

### For Development
1. Code in `app/` - All modules have docstrings
2. `app/guards.py` - See how policies work
3. `demo/tests/test_config.py` - See example tests

## Step 7: Try Custom Edits (5 minutes)

1. Switch to **"Custom edit"** mode
2. Enter a file path: `config/app.yaml`
3. Enter intent: `increase timeout`
4. Type new contents:
   ```yaml
   service: web
   pagination: 50
   featureX: false
   timeout: 30
   ```
5. Click **"Run with Aegis"**

**What happens?** Aegis will check if `timeout` is an allowed key in the policy. If not, it blocks. If yes, it runs tests.

## Common Questions

**Q: Do I need API keys?**  
A: No! Aegis works completely offline. API keys are optional for AI explanations and cloud sandbox.

**Q: Where are the docs?**  
A: Click "📖 Architecture" or "🚀 Walkthrough" in the UI header, or see `docs/` folder.

**Q: How do I stop the app?**  
A: Press `Ctrl+C` in the terminal where you ran `bash scripts/dev.sh`

**Q: Can I use my own repo?**  
A: Yes! See "Samples" tab or `docs/ARCHITECTURE.md` section on repository structure.

**Q: What if something breaks?**  
A: Check `README.md` Troubleshooting section, or look at terminal logs.

## Next Steps

- ✅ Try all three presets (Unsafe delete, Safe pagination, Safe rollout)
- ✅ Read `docs/ARCHITECTURE.md` to understand the system
- ✅ Follow `docs/WALKTHROUGH.md` for hands-on examples
- ✅ Modify `app/guards.py` to add your own policy rules
- ✅ Add tests to `demo/tests/` to see how validation works

**Welcome to Aegis! 🛡️**

