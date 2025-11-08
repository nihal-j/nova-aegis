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
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/nova-aegis",
            "X-Title": "Nova Aegis"
        }
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more consistent, factual explanations
            "max_tokens": 500  # Allow longer explanations
        }
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        result = response.json()
        # Extract the content from the response
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"].strip()
            if content:
                return content
        return ""
    except requests.exceptions.RequestException as e:
        # Log specific error for debugging
        print(f"OpenRouter API error: {type(e).__name__}: {str(e)[:200]}")
        return ""
    except Exception as e:
        # Log unexpected errors
        print(f"OpenRouter unexpected error: {type(e).__name__}: {str(e)[:200]}")
        return ""

