"""
OpenRouter API client for Aegis.

Calls OpenRouter API to get AI-powered explanations using Claude 3.5 Sonnet.
Handles errors gracefully - returns empty string on any failure.

Requires:
- OpenRouter API key in OPENROUTER_API_KEY.txt
"""
import requests


def call_openrouter(prompt: str, api_key: str) -> str:
    """
    Call OpenRouter API with the given prompt.
    Returns empty string on any error.
    """
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/nova-aegis",
            "X-Title": "Nova Aegis"
        }
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        result = response.json()
        # Extract the content from the response
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        return ""
    except Exception:
        return ""

