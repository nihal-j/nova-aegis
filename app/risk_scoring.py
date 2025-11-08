"""Risk scoring system for Aegis."""
from typing import Dict, List, Tuple


def calculate_risk_score(risk_card: dict) -> int:
    """
    Calculate risk score (0-100) from risk card data.
    
    Scoring factors:
    - Base: 50 if blocked, 10 if allowed
    - Failed checks: +15 per failure
    - Policy failures: +20 extra
    - Test failures: +25 extra
    - Risky patterns: +8-15 per pattern
    - Large deletions: +15 if >10 lines
    
    Args:
        risk_card: Risk card dictionary with checks, status, diff
        
    Returns:
        Integer score 0-100 (capped)
    """
    checks = risk_card.get("checks", [])
    status = risk_card.get("status", "unknown")
    diff = risk_card.get("diff", "")
    
    score = 0
    
    # Base score from status
    if status == "blocked":
        score += 50
    elif status == "allow":
        score += 10
    
    # Failed checks add to score
    failed_checks = [name for name, ok, msg in checks if not ok]
    score += len(failed_checks) * 15
    
    # Policy failures are more serious
    for name, ok, msg in checks:
        if not ok and name == "policy":
            score += 20
        elif not ok and name == "dry_run_tests":
            score += 25
    
    # Analyze diff for risky patterns
    if diff:
        risky_patterns = [
            ("DELETE", 10),
            ("DROP", 10),
            ("rm -rf", 15),
            ("DROP TABLE", 15),
            ("TRUNCATE", 12),
            ("--force", 8),
            ("--no-check", 8),
        ]
        diff_upper = diff.upper()
        for pattern, penalty in risky_patterns:
            if pattern in diff_upper:
                score += penalty
    
    # Large deletions are risky
    if diff:
        lines = diff.split("\n")
        deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
        if deletions > 10:
            score += min(15, deletions // 5)
    
    # Airia AI risk adjustment (if available)
    diff_analysis = risk_card.get("diff_analysis", {})
    if diff_analysis.get("ai_enhanced"):
        try:
            from app.airia_analysis import get_airia_risk_adjustment
            score += get_airia_risk_adjustment(diff_analysis)
        except Exception:
            pass  # Silently ignore if Airia module has issues
    
    # Cap at 100
    return min(100, max(0, score))


def get_risk_level(score: int) -> Tuple[str, str]:
    """Get risk level name and color from score."""
    if score < 20:
        return "LOW", "green"
    elif score < 50:
        return "MEDIUM", "yellow"
    elif score < 80:
        return "HIGH", "orange"
    else:
        return "CRITICAL", "red"

