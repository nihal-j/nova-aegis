"""
Airia AI-powered code analysis integration for Aegis.

Enhances diff analysis, risk scoring, and explanations with AI-powered insights.
Gracefully falls back to basic functionality if Airia is not configured.

Requires:
- Airia package installed (pip install airia) - optional
- AIRIA_API_KEY in AIRIA_API_KEY.txt - optional

All functions return None or empty results if Airia is unavailable - no errors thrown.
"""
from typing import Dict, List, Optional
from app.secrets import _PROJECT_ROOT
from pathlib import Path


def is_airia_available() -> bool:
    """Check if Airia is configured and available."""
    try:
        from airia import AiriaClient
        api_key = read_airia_key()
        return api_key is not None and api_key.strip() != ""
    except ImportError:
        return False
    except Exception:
        return False


def read_airia_key() -> Optional[str]:
    """Read Airia API key from AIRIA_API_KEY.txt."""
    possible_paths = [
        _PROJECT_ROOT / "AIRIA_API_KEY.txt",
        Path("AIRIA_API_KEY.txt"),
    ]
    
    for p in possible_paths:
        if p.exists():
            try:
                key = p.read_text().strip()
                if key:
                    return key
            except Exception:
                continue
    return None


def get_airia_risk_adjustment(diff_analysis: Dict) -> int:
    """
    Get risk score adjustment based on Airia AI analysis.
    
    Args:
        diff_analysis: Enhanced diff analysis dictionary
        
    Returns:
        Integer adjustment to risk score (can be negative to reduce risk, positive to increase)
    """
    if not diff_analysis.get("ai_enhanced"):
        return 0
    
    adjustment = 0
    ai_risks = diff_analysis.get("ai_risks", [])
    ai_confidence = diff_analysis.get("ai_confidence", 0.5)
    
    # High confidence AI risks increase score
    if ai_risks:
        # More risks = higher adjustment
        adjustment += len(ai_risks) * 5
        # High confidence = more weight
        if ai_confidence > 0.7:
            adjustment += 10
        elif ai_confidence > 0.5:
            adjustment += 5
    
    return min(20, adjustment)  # Cap adjustment at +20


def analyze_with_airia(diff: str, file_path: str, intent: str) -> Optional[Dict]:
    """
    Use Airia AI to analyze code changes for security and quality issues.
    
    Args:
        diff: Unified diff string
        file_path: Path to the file being modified
        intent: User's intent for the change
        
    Returns:
        Dictionary with AI analysis results, or None if Airia unavailable:
        - ai_risks: List[str] - AI-detected security/quality risks
        - ai_confidence: float - Confidence score (0-1)
        - ai_recommendations: List[str] - AI suggestions
        - ai_summary: str - AI-generated summary
    """
    api_key = read_airia_key()
    if not api_key:
        return None
    
    try:
        from airia import AiriaClient
        
        client = AiriaClient(api_key=api_key)
        
        # Build prompt for AI code review
        prompt = f"""Analyze this code change for security risks, quality issues, and potential problems.

File: {file_path}
Intent: {intent}

Diff:
{diff[:2000]}  # Limit to first 2000 chars

Provide:
1. Security risks (SQL injection, XSS, secrets exposure, etc.)
2. Code quality issues (performance, maintainability, bugs)
3. Recommendations for improvement
4. Overall risk assessment (low/medium/high)

Format as JSON with keys: risks, confidence, recommendations, summary."""
        
        # Use Airia's pipeline execution for code analysis
        # Note: This is a placeholder - adjust based on actual Airia API
        try:
            # Option 1: Use Airia's AI Gateway for analysis
            response = client.pipelines.execute_pipeline(
                pipeline_id="code-review",  # You'd configure this in Airia
                inputs={
                    "diff": diff[:2000],
                    "file_path": file_path,
                    "intent": intent
                }
            )
            
            # Parse response (adjust based on actual Airia response format)
            if response and "output" in response:
                output = response["output"]
                return {
                    "ai_risks": output.get("risks", []),
                    "ai_confidence": output.get("confidence", 0.5),
                    "ai_recommendations": output.get("recommendations", []),
                    "ai_summary": output.get("summary", "AI analysis completed")
                }
        except Exception as e:
            # If pipeline doesn't exist, fall back to basic AI call
            # This would use Airia's general AI capabilities
            print(f"Airia pipeline error (falling back): {e}")
            return None
            
    except ImportError:
        # Airia not installed - silently fail
        return None
    except Exception as e:
        # Any other error - silently fail (don't print to avoid UI noise)
        return None
    
    return None


def enhance_explanation_with_airia(explanation: str, diff_analysis: Dict) -> str:
    """
    Enhance explanation with Airia AI insights if available.
    
    Args:
        explanation: Current explanation text
        diff_analysis: Enhanced diff analysis with AI insights
        
    Returns:
        Enhanced explanation string
    """
    if not diff_analysis.get("ai_enhanced"):
        return explanation
    
    ai_summary = diff_analysis.get("ai_summary", "")
    ai_recommendations = diff_analysis.get("ai_recommendations", [])
    
    if not ai_summary and not ai_recommendations:
        return explanation
    
    # Append AI insights to explanation
    enhanced = explanation
    if ai_summary:
        enhanced += f"\n\n🤖 AI Analysis: {ai_summary}"
    if ai_recommendations:
        enhanced += f"\n💡 Recommendations: {'; '.join(ai_recommendations[:3])}"  # Limit to 3
    
    return enhanced


def enhance_diff_analysis(basic_analysis: Dict, diff: str, file_path: str, intent: str) -> Dict:
    """
    Enhance basic diff analysis with Airia AI insights.
    
    Args:
        basic_analysis: Results from analyze_diff()
        diff: Unified diff string
        file_path: Path to file being modified
        intent: User's intent
        
    Returns:
        Enhanced analysis dictionary with AI insights added
    """
    # Get AI analysis if available
    ai_analysis = analyze_with_airia(diff, file_path, intent)
    
    if ai_analysis:
        # Merge AI insights into basic analysis
        basic_analysis["ai_enhanced"] = True
        basic_analysis["ai_risks"] = ai_analysis.get("ai_risks", [])
        basic_analysis["ai_confidence"] = ai_analysis.get("ai_confidence", 0.5)
        basic_analysis["ai_recommendations"] = ai_analysis.get("ai_recommendations", [])
        basic_analysis["ai_summary"] = ai_analysis.get("ai_summary", "")
        
        # Add AI-detected risks to risky_patterns
        if ai_analysis.get("ai_risks"):
            basic_analysis["risky_patterns"].extend([
                f"AI: {risk}" for risk in ai_analysis["ai_risks"]
            ])
    else:
        basic_analysis["ai_enhanced"] = False
    
    return basic_analysis

