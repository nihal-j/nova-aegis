"""Advanced diff analysis for Aegis."""
from typing import Dict, List, Tuple


def analyze_diff(diff: str) -> Dict:
    """
    Analyze a unified diff for risky patterns and change statistics.
    
    Args:
        diff: Unified diff string (from difflib.unified_diff)
        
    Returns:
        Dictionary with keys:
        - lines_added: int - Number of lines added
        - lines_removed: int - Number of lines removed
        - risky_patterns: List[str] - Detected risky patterns (DELETE, DROP, etc.)
        - sensitive_data: bool - True if potential secrets detected
        - summary: str - Human-readable summary
        - added_lines: List[str] - First 10 added lines (preview)
        - removed_lines: List[str] - First 10 removed lines (preview)
    """
    if not diff:
        return {
            "lines_added": 0,
            "lines_removed": 0,
            "risky_patterns": [],
            "sensitive_data": False,
            "summary": "No changes detected"
        }
    
    lines = diff.split("\n")
    added = []
    removed = []
    
    for line in lines:
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:])
    
    # Check for risky patterns
    risky_patterns = []
    all_text = "\n".join(added + removed).upper()
    
    patterns = {
        "DELETE": "DELETE statement detected",
        "DROP": "DROP statement detected",
        "TRUNCATE": "TRUNCATE statement detected",
        "rm -rf": "Recursive delete command",
        "--force": "Force flag detected",
        "--no-check": "Safety check bypass",
        "password": "Potential password exposure",
        "secret": "Potential secret exposure",
        "api_key": "Potential API key exposure",
        "token": "Potential token exposure",
    }
    
    for pattern, description in patterns.items():
        if pattern in all_text:
            risky_patterns.append(description)
    
    # Check for sensitive data patterns
    sensitive_patterns = ["password", "secret", "api_key", "token", "credential"]
    sensitive_data = any(p in all_text.lower() for p in sensitive_patterns)
    
    # Generate summary
    summary_parts = []
    if len(added) > 0:
        summary_parts.append(f"{len(added)} line(s) added")
    if len(removed) > 0:
        summary_parts.append(f"{len(removed)} line(s) removed")
    if risky_patterns:
        summary_parts.append(f"{len(risky_patterns)} risky pattern(s) found")
    
    summary = ", ".join(summary_parts) if summary_parts else "No significant changes"
    
    return {
        "lines_added": len(added),
        "lines_removed": len(removed),
        "risky_patterns": risky_patterns,
        "sensitive_data": sensitive_data,
        "summary": summary,
        "added_lines": added[:10],  # First 10 for preview
        "removed_lines": removed[:10]
    }

