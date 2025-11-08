"""Webhook integration system for Aegis."""
import requests
import os
from typing import Dict, Optional


def send_webhook(risk_card: dict, webhook_url: Optional[str] = None) -> bool:
    """
    Send webhook notification about a risk card.
    
    Args:
        risk_card: Risk card dictionary to send
        webhook_url: Optional URL (defaults to AEGIS_WEBHOOK_URL env var)
        
    Returns:
        True if webhook sent successfully, False otherwise
        
    Side effects:
        Makes HTTP POST request to webhook URL
    """
    if webhook_url is None:
        webhook_url = os.getenv("AEGIS_WEBHOOK_URL")
    
    if not webhook_url:
        return False
    
    try:
        status = risk_card.get("status", "unknown")
        risk_score = risk_card.get("risk_score", 0)
        checks = risk_card.get("checks", [])
        failed = [name for name, ok, msg in checks if not ok]
        
        payload = {
            "status": status,
            "risk_score": risk_score,
            "failed_checks": failed,
            "explanation": risk_card.get("explanation", ""),
            "timestamp": risk_card.get("ts", 0)
        }
        
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception:
        return False

