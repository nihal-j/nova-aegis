"""
Policy validation module for Aegis.

Enforces safety rules on proposed actions:
- File path allowlisting (only config/ and flags/ allowed)
- Intent validation (blocks destructive operations)
- Content structure validation (YAML/JSON schema checks)

See docs/ARCHITECTURE.md for policy rule examples.
"""
ALLOWED_PATHS = ["config", "flags"]

def policy_check(action: dict):
    """
    Validate a proposed action against policy rules.
    
    Args:
        action: Dictionary with keys: file_path, intent, new_contents
        
    Returns:
        Tuple of (passed: bool, message: str)
        - (True, "OK") if all checks pass
        - (False, reason) if any check fails
    """
    fp = action.get("file_path","")
    # Only allow editing files under config/ or flags/
    if not any(fp == p or fp.startswith(p + "/") for p in ALLOWED_PATHS):
        return False, f"File '{fp}' not in allowlist {ALLOWED_PATHS}"
    # Block obviously destructive intents
    if "delete" in action.get("intent","").lower():
        return False, "Destructive intent blocked"

    # Key allowlists with types/ranges (kid-simple)
    if fp == "config/app.yaml":
        import yaml
        try:
            data = yaml.safe_load(action.get("new_contents","")) or {}
        except Exception as e:
            return False, f"YAML parse error: {e}"
        allowed = {"service": str, "pagination": int, "featureX": bool}
        for k,v in data.items():
            if k not in allowed: return False, f"Key '{k}' not allowed in app.yaml"
            if k=="pagination" and not (1 <= int(v) <= 100):
                return False, "pagination must be 1..100"
            if k=="service" and not isinstance(v, str):
                return False, "service must be a string"
            if k=="featureX" and not isinstance(v, bool):
                return False, "featureX must be true/false"

    if fp == "flags/rollout.json":
        import json
        try:
            data = json.loads(action.get("new_contents",""))
        except Exception as e:
            return False, f"JSON parse error: {e}"
        try:
            pct = int(data["featureX"]["percentage"])
        except Exception:
            return False, "flags must have featureX.percentage"
        if not (0 <= pct <= 50):
            return False, "percentage must be 0..50 (no instant 100%)"

    return True, "OK"
