"""
Explanation generation for Aegis.

Generates human-readable explanations of risk assessments. Uses OpenRouter
(Claude 3.5 Sonnet) if API key is available, otherwise builds plain-English
explanations from checks and diff analysis.

Always returns a string - never crashes, even if OpenRouter fails.
"""
from app.secrets import read_openrouter_key
from app.openrouter import call_openrouter


def explain_reason(risk_card: dict, max_chars: int = 400) -> str:
    """
    Generate a clear, specific explanation of the risk assessment.
    Uses OpenRouter if API key is available, otherwise builds a detailed plain-English explanation.
    Never crashes; always returns a string.
    """
    try:
        # Try OpenRouter first if key is available
        api_key = read_openrouter_key()
        if api_key and api_key.strip():
            try:
                # Build detailed prompt for OpenRouter with full context
                checks = risk_card.get("checks", [])
                status = risk_card.get("status", "unknown")
                diff = risk_card.get("diff", "")
                action = risk_card.get("action", {})
                file_path = action.get("file_path", "unknown")
                intent = action.get("intent", "unknown")
                
                # Build detailed check summary
                check_details = []
                for name, ok, msg in checks:
                    if not ok:
                        check_details.append(f"FAILED: {name.upper()} check - {msg}")
                    else:
                        check_details.append(f"PASSED: {name.upper()} check - {msg}")
                
                check_summary = "\n".join(check_details)
                
                # Extract diff details
                diff_summary = ""
                if diff:
                    lines = diff.split("\n")
                    added = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
                    removed = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
                    diff_summary = f"\n\nCode Changes:\n- {added} lines added\n- {removed} lines removed"
                    # Include first few lines of actual diff for context
                    diff_preview = "\n".join([line for line in lines[:10] if line.strip() and not line.startswith("@@")])
                    if diff_preview:
                        diff_summary += f"\n\nPreview of changes:\n{diff_preview}"
                
                # Build comprehensive prompt
                prompt = f"""You are a security analyst explaining a code change risk assessment. Provide a clear, specific explanation.

ACTION DETAILS:
- File: {file_path}
- Intent: {intent}
- Status: {status.upper()}

CHECK RESULTS:
{check_summary}
{diff_summary}

INSTRUCTIONS:
1. If BLOCKED: Explain SPECIFICALLY which check failed and why it's dangerous. Mention the exact policy rule or test that failed.
2. If ALLOWED: Explain why all checks passed and why this change is safe.
3. Be specific about what would happen if this change was applied.
4. Use plain English, be concise but informative (max {max_chars} characters).

Example for blocked: "This action was BLOCKED because the policy check failed. The intent contains 'delete', which violates the destructive operation policy. This prevents accidental deletion of critical resources."

Example for allowed: "This action is SAFE. The policy check passed (file path is allowed, intent is safe). The sandbox tests passed, confirming the change works correctly. The pagination value (50) is within the allowed range (1-100)."

Now provide the explanation:"""
                
                explanation = call_openrouter(prompt, api_key)
                if explanation and explanation.strip():
                    # Truncate to max_chars if needed
                    if len(explanation) > max_chars:
                        explanation = explanation[:max_chars-3] + "..."
                    return explanation.strip()
            except Exception as e:
                # Log error but don't crash - fall through to local explanation
                print(f"OpenRouter error (falling back to local): {e}")
                pass
        
        # Build detailed local explanation from checks and diff
        checks = risk_card.get("checks", [])
        status = risk_card.get("status", "unknown")
        diff = risk_card.get("diff", "")
        action = risk_card.get("action", {})
        file_path = action.get("file_path", "unknown file")
        intent = action.get("intent", "unknown intent")
        
        # Summarize checks with specific error messages
        passed = [(name, msg) for name, ok, msg in checks if ok]
        failed = [(name, msg) for name, ok, msg in checks if not ok]
        
        parts = []
        
        if status == "allow":
            parts.append("✅ This action is SAFE and has been ALLOWED.")
            if passed:
                passed_details = []
                for name, msg in passed:
                    if name == "policy":
                        passed_details.append("policy validation passed (file path allowed, intent is safe, content structure valid)")
                    elif name == "dry_run_tests":
                        passed_details.append("all tests passed in sandbox")
                    elif name == "modal":
                        passed_details.append("cloud sandbox executed successfully")
                    else:
                        passed_details.append(f"{name} check passed")
                parts.append("All safety checks passed: " + "; ".join(passed_details))
            
            # Add context about what was validated
            if file_path != "unknown file":
                parts.append(f"The change to '{file_path}' was validated and is safe to apply.")
        else:
            parts.append("⛔ This action is BLOCKED and cannot proceed.")
            
            if failed:
                # Build detailed failure explanations
                failure_explanations = []
                for name, msg in failed:
                    if name == "policy":
                        if "not in allowlist" in msg:
                            failure_explanations.append(f"Policy violation: The file path '{file_path}' is not in the allowed list. Only files under 'config/' or 'flags/' can be modified for safety.")
                        elif "Destructive intent blocked" in msg:
                            failure_explanations.append(f"Policy violation: The intent '{intent}' contains 'delete', which is blocked by the destructive operation policy. This prevents accidental deletion of critical resources.")
                        elif "not allowed in app.yaml" in msg:
                            failure_explanations.append(f"Policy violation: {msg}. Only specific keys (service, pagination, featureX) are allowed in app.yaml for security.")
                        elif "pagination must be" in msg:
                            failure_explanations.append(f"Policy violation: {msg}. Pagination values must be between 1-100 to prevent performance issues or broken pagination.")
                        elif "percentage must be" in msg:
                            failure_explanations.append(f"Policy violation: {msg}. Rollout percentages are capped at 50% to prevent instant 100% rollouts that could break production.")
                        elif "parse error" in msg:
                            failure_explanations.append(f"Policy violation: {msg}. The file content is not valid YAML/JSON.")
                        else:
                            failure_explanations.append(f"Policy violation: {msg}")
                    elif name == "dry_run_tests":
                        failure_explanations.append(f"Test failure: The sandbox tests failed. {msg if msg and msg != 'tests failed' else 'One or more validation tests did not pass, indicating the change may cause issues.'}")
                    elif name == "modal":
                        failure_explanations.append(f"Modal sandbox unavailable: {msg}. Falling back to local sandbox.")
                    else:
                        failure_explanations.append(f"{name} check failed: {msg if msg else 'Unknown error'}")
                
                if failure_explanations:
                    parts.append("Reason: " + " ".join(failure_explanations))
                else:
                    parts.append(f"One or more safety checks failed: {', '.join([name for name, _ in failed])}")
            
            # Add context about what was blocked
            if file_path != "unknown file":
                parts.append(f"The proposed change to '{file_path}' cannot be applied due to the above safety violations.")
        
        # Add diff summary if available
        if diff:
            lines = diff.split("\n")
            added = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
            removed = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
            if added > 0 or removed > 0:
                parts.append(f"Change summary: {added} line(s) added, {removed} line(s) removed.")
        
        explanation = " ".join(parts)
        
        # Truncate to max_chars if needed
        if len(explanation) > max_chars:
            explanation = explanation[:max_chars-3] + "..."
        
        return explanation
        
    except Exception:
        # Ultimate fallback - never crash
        return "Risk assessment completed."

