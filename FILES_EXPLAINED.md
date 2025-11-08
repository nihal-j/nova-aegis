# 📁 Complete File Explanation

Every file in the Aegis project, explained.

## 🚨 **BEFORE PUSHING TO GITHUB - READ THIS**

### ✅ **SAFE TO PUSH** (All these are in `.gitignore`):
- `.env` - Contains your API keys (gitignored)
- `OPENROUTER_API_KEY.txt` - Contains OpenRouter API key (gitignored)
- `aegis_history.db` - SQLite database with history (gitignored)
- `venv/` or `.venv/` - Virtual environment (gitignored)
- `__pycache__/` - Python cache files (gitignored)

### ⚠️ **CHECK BEFORE PUSHING**:
1. Run: `git status` - Make sure `.env`, `OPENROUTER_API_KEY.txt`, and `*.db` files are NOT listed
2. If they ARE listed, they're not gitignored - **DO NOT PUSH**
3. If you see them in `git status`, add them: `git restore --staged .env OPENROUTER_API_KEY.txt aegis_history.db`

---

## 📂 Root Directory Files

### `README.md`
**Purpose:** Main project documentation and quickstart guide  
**Contains:** 
- "New User? Start Here!" section
- 5-minute quickstart
- 60-second demo steps
- Features, configuration, troubleshooting
- API endpoints reference

**Safe to push?** ✅ YES - Public documentation

---

### `ONBOARDING.md`
**Purpose:** Complete step-by-step guide for brand new users  
**Contains:**
- What Aegis is (explained simply)
- Installation steps
- First test walkthrough
- UI exploration guide
- Learning path

**Safe to push?** ✅ YES - Public documentation

---

### `.gitignore`
**Purpose:** Tells Git which files to ignore  
**Contains:**
- `venv/`, `.venv/` - Virtual environments
- `.env` - Environment variables (may contain secrets)
- `OPENROUTER_API_KEY.txt` - API key file
- `*.db`, `aegis_history.db` - Database files
- `__pycache__/` - Python cache

**Safe to push?** ✅ YES - This file should be committed

---

### `requirements.txt`
**Purpose:** Python package dependencies  
**Contains:**
- List of all required packages (fastapi, streamlit, pydantic, etc.)
- Version pins (if any)

**Safe to push?** ✅ YES - Required for installation

---

### `create_key_file.py`
**Purpose:** Helper script to create `OPENROUTER_API_KEY.txt`  
**Contains:**
- Prompts user for API key
- Creates the key file
- Does NOT contain any keys

**Safe to push?** ✅ YES - Just a helper script

---

### `.env` ⚠️ **DO NOT PUSH**
**Purpose:** Environment variables  
**Contains:**
- `DEMO_REPO` - GitHub repo URL (public, safe)
- `OPENROUTER_API_KEY` - API key (SECRET - but empty in your case)
- `AEGIS_WEBHOOK_URL` - Optional webhook URL

**Safe to push?** ❌ NO - Even if empty, should stay local  
**Status:** ✅ In `.gitignore` - Won't be pushed

---

### `OPENROUTER_API_KEY.txt` ⚠️ **DO NOT PUSH**
**Purpose:** Stores OpenRouter API key  
**Contains:**
- Your OpenRouter API key (if you added one)

**Safe to push?** ❌ NO - Contains secrets  
**Status:** ✅ In `.gitignore` - Won't be pushed

---

### `aegis_history.db` ⚠️ **DO NOT PUSH**
**Purpose:** SQLite database storing risk card history  
**Contains:**
- All past risk assessments
- Request IDs, timestamps, risk scores
- May contain sensitive data from past tests

**Safe to push?** ❌ NO - Contains runtime data  
**Status:** ✅ In `.gitignore` - Won't be pushed

---

## 📂 `app/` Directory - Backend API

### `app/app.py`
**Purpose:** Main FastAPI application  
**Contains:**
- FastAPI app initialization
- All API endpoints (`/health`, `/propose_action`, `/riskcard`, etc.)
- Orchestrates policy → sandbox → scoring → explanation flow
- Modal error handling

**Safe to push?** ✅ YES - Core application code

---

### `app/guards.py`
**Purpose:** Policy validation rules  
**Contains:**
- `policy_check()` function
- File path allowlisting (only `config/` and `flags/`)
- Intent validation (blocks "delete", "drop", etc.)
- Content schema validation

**Safe to push?** ✅ YES - Policy rules (no secrets)

---

### `app/dryrun_local.py`
**Purpose:** Local sandbox execution  
**Contains:**
- `dry_run()` function
- Creates temp directory
- Copies `demo/` directory
- Applies changes and runs pytest
- Generates unified diff

**Safe to push?** ✅ YES - Sandbox logic (no secrets)

---

### `app/modal_runner.py`
**Purpose:** Modal cloud sandbox execution  
**Contains:**
- Modal function definition
- Clones remote repo
- Runs tests in cloud
- Returns results

**Safe to push?** ✅ YES - Cloud sandbox code (no secrets)

---

### `app/explain.py`
**Purpose:** Generates risk assessment explanations  
**Contains:**
- `explain_reason()` function
- Tries OpenRouter API first
- Falls back to plain-English explanations
- Never crashes

**Safe to push?** ✅ YES - Explanation logic (reads key from file, doesn't store it)

---

### `app/openrouter.py`
**Purpose:** OpenRouter API client  
**Contains:**
- `call_openrouter()` function
- Makes HTTP requests to OpenRouter
- Handles errors gracefully

**Safe to push?** ✅ YES - API client (takes key as parameter, doesn't store it)

---

### `app/secrets.py`
**Purpose:** Reads API keys from files  
**Contains:**
- `read_openrouter_key()` function
- Reads from `OPENROUTER_API_KEY.txt`
- Returns `None` if file doesn't exist

**Safe to push?** ✅ YES - Just reads files, doesn't contain keys

---

### `app/risk_scoring.py`
**Purpose:** Calculates risk scores (0-100)  
**Contains:**
- `calculate_risk_score()` function
- Scoring algorithm based on checks, patterns, diff analysis
- Returns risk level (LOW/MEDIUM/HIGH/CRITICAL)

**Safe to push?** ✅ YES - Scoring logic (no secrets)

---

### `app/diff_analysis.py`
**Purpose:** Analyzes code diffs for risky patterns  
**Contains:**
- `analyze_diff()` function
- Detects DELETE, DROP, TRUNCATE statements
- Detects potential secret exposure
- Counts lines added/removed

**Safe to push?** ✅ YES - Analysis logic (no secrets)

---

### `app/history.py`
**Purpose:** SQLite database operations for risk card history  
**Contains:**
- `save_risk_card()` - Saves to database
- `get_risk_card()` - Retrieves by request_id
- `get_history()` - Gets recent history
- `approve_risk_card()` - Marks as approved

**Safe to push?** ✅ YES - Database operations (no secrets, database file is gitignored)

---

### `app/metrics.py`
**Purpose:** Performance metrics tracking  
**Contains:**
- `record_request()` - Records API request metrics
- `get_metrics()` - Returns aggregated stats
- In-memory storage (last 1000 entries)

**Safe to push?** ✅ YES - Metrics tracking (no secrets)

---

### `app/webhooks.py`
**Purpose:** Sends webhook notifications  
**Contains:**
- `send_webhook()` function
- Reads webhook URL from environment
- Sends POST request with risk card data

**Safe to push?** ✅ YES - Webhook logic (reads URL from env, doesn't store it)

---

## 📂 `ui/` Directory - Frontend

### `ui/ui.py`
**Purpose:** Streamlit web UI  
**Contains:**
- Dark-themed UI with gradients
- Action Builder (left panel)
- Risk Card display (right panel)
- Samples tab
- Welcome panel for new users
- Help tooltips
- Docs links in header

**Safe to push?** ✅ YES - Frontend code (no secrets)

---

## 📂 `demo/` Directory - Demo Repository

### `demo/config/app.yaml`
**Purpose:** Example configuration file  
**Contains:**
- Sample YAML config
- Used for testing policy validation

**Safe to push?** ✅ YES - Example data (no secrets)

---

### `demo/flags/rollout.json`
**Purpose:** Example feature flags file  
**Contains:**
- Sample JSON feature flags
- Used for testing policy validation

**Safe to push?** ✅ YES - Example data (no secrets)

---

### `demo/tests/test_config.py`
**Purpose:** Example pytest tests  
**Contains:**
- Tests that validate config files
- Tests pagination ranges
- Tests rollout percentages

**Safe to push?** ✅ YES - Example tests (no secrets)

---

## 📂 `docs/` Directory - Documentation

### `docs/ARCHITECTURE.md`
**Purpose:** System architecture documentation  
**Contains:**
- High-level overview
- Mermaid sequence diagrams
- Component diagrams
- Risk Card JSON schema
- Repository structure guide
- Secrets model explanation
- FAQ section

**Safe to push?** ✅ YES - Public documentation

---

### `docs/WALKTHROUGH.md`
**Purpose:** Hands-on tutorial  
**Contains:**
- Step-by-step setup
- curl examples
- Modal setup guide
- How to add tests
- How to modify policies
- "Ship it" checklist

**Safe to push?** ✅ YES - Public documentation

---

## 📂 `scripts/` Directory - Utility Scripts

### `scripts/dev.sh`
**Purpose:** Development server launcher  
**Contains:**
- Starts FastAPI backend (uvicorn)
- Starts Streamlit frontend
- Prints banner with URLs
- Handles Ctrl+C gracefully

**Safe to push?** ✅ YES - Development script (no secrets)

---

### `scripts/curl-examples.sh`
**Purpose:** Example curl commands for API  
**Contains:**
- Health check example
- Unsafe action example
- Safe action example
- History endpoint example
- All commented and formatted

**Safe to push?** ✅ YES - Example commands (no secrets)

---

## 🔒 Security Checklist Before Pushing

Run these commands before `git push`:

```bash
# 1. Check what Git sees
git status

# 2. Make sure these are NOT listed (they should be ignored):
# - .env
# - OPENROUTER_API_KEY.txt
# - aegis_history.db
# - *.db
# - venv/
# - .venv/

# 3. If any of the above ARE listed, unstage them:
git restore --staged .env OPENROUTER_API_KEY.txt aegis_history.db

# 4. Verify .gitignore is correct
cat .gitignore | grep -E "(\.env|OPENROUTER|\.db|venv)"

# 5. If everything looks good, you're safe to push!
```

---

## 📍 Onboarding Flow Clarification

### **Where does onboarding happen?**

**Two places:**

1. **GitHub README** (`README.md`)
   - First thing users see when they visit the repo
   - "New User? Start Here!" section at the top
   - Quick 5-minute quickstart
   - Links to deeper docs

2. **Local UI** (after running `bash scripts/dev.sh`)
   - Welcome panel appears in the Risk Card (right side)
   - Interactive introduction
   - "🎓 New User Guide" link in header
   - Samples tab with examples

**Flow:**
1. User finds repo on GitHub → Reads `README.md`
2. User clones repo → Follows quickstart in `README.md`
3. User runs `bash scripts/dev.sh` → Opens http://127.0.0.1:8501
4. User sees welcome panel → Clicks "🎓 New User Guide" for `ONBOARDING.md`
5. User explores UI → Tries presets, reads docs

**Both are needed:**
- GitHub README = First impression, gets them started
- Local UI = Interactive experience, hands-on learning

---

## ✅ Final Safety Check

**Before pushing, verify:**

```bash
# Check what will be committed
git status

# Should see:
# ✅ README.md
# ✅ ONBOARDING.md
# ✅ .gitignore
# ✅ requirements.txt
# ✅ app/*.py (all files)
# ✅ ui/ui.py
# ✅ demo/**/* (all files)
# ✅ docs/**/*.md (all files)
# ✅ scripts/*.sh (all files)
# ✅ create_key_file.py

# Should NOT see:
# ❌ .env
# ❌ OPENROUTER_API_KEY.txt
# ❌ aegis_history.db
# ❌ venv/
# ❌ .venv/
# ❌ __pycache__/
```

**If everything above checks out → ✅ SAFE TO PUSH!**

