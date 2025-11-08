"""Performance metrics tracking for Aegis."""
import time
from typing import Dict, List
from collections import defaultdict

_metrics = {
    "requests": [],
    "execution_times": [],
    "errors": []
}


def record_request(endpoint: str, execution_time: float, success: bool, error: str = None):
    """
    Record a request metric for performance tracking.
    
    Args:
        endpoint: API endpoint path (e.g., "/propose_action")
        execution_time: Request duration in seconds
        success: True if request succeeded
        error: Optional error message if failed
        
    Side effects:
        Updates in-memory metrics dictionary (keeps last 1000 entries)
    """
    _metrics["requests"].append({
        "endpoint": endpoint,
        "timestamp": time.time(),
        "execution_time": execution_time,
        "success": success
    })
    _metrics["execution_times"].append(execution_time)
    
    if error:
        _metrics["errors"].append({
            "endpoint": endpoint,
            "timestamp": time.time(),
            "error": error
        })
    
    # Keep only last 1000 entries
    if len(_metrics["requests"]) > 1000:
        _metrics["requests"] = _metrics["requests"][-1000:]
    if len(_metrics["execution_times"]) > 1000:
        _metrics["execution_times"] = _metrics["execution_times"][-1000:]
    if len(_metrics["errors"]) > 100:
        _metrics["errors"] = _metrics["errors"][-100:]


def get_metrics() -> Dict:
    """Get aggregated metrics."""
    if not _metrics["execution_times"]:
        return {
            "total_requests": 0,
            "avg_execution_time": 0,
            "total_errors": 0,
            "endpoints": {}
        }
    
    endpoint_stats = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})
    
    for req in _metrics["requests"]:
        endpoint_stats[req["endpoint"]]["count"] += 1
        endpoint_stats[req["endpoint"]]["total_time"] += req["execution_time"]
        if not req["success"]:
            endpoint_stats[req["endpoint"]]["errors"] += 1
    
    endpoints = {}
    for endpoint, stats in endpoint_stats.items():
        endpoints[endpoint] = {
            "count": stats["count"],
            "avg_time": stats["total_time"] / stats["count"] if stats["count"] > 0 else 0,
            "errors": stats["errors"]
        }
    
    return {
        "total_requests": len(_metrics["requests"]),
        "avg_execution_time": sum(_metrics["execution_times"]) / len(_metrics["execution_times"]),
        "total_errors": len(_metrics["errors"]),
        "endpoints": endpoints
    }

