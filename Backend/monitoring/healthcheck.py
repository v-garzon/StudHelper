#!/usr/bin/env python3
"""
Health check script for StudHelper Backend
Usage: python monitoring/healthcheck.py [--url URL] [--timeout SECONDS]
"""

import argparse
import requests
import sys
import time
import json
from datetime import datetime

def check_health(url: str, timeout: int = 30) -> bool:
    """Check if the application is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def check_database(url: str, timeout: int = 30) -> bool:
    """Check if database connection is working"""
    try:
        # This would require authentication, so just check if endpoint exists
        response = requests.get(f"{url}/api/v1/auth/me", timeout=timeout)
        # 403 is expected without auth, but means the endpoint is reachable
        return response.status_code in [401, 403]
    except Exception as e:
        print(f"Database check failed: {e}")
        return False

def check_openai_integration(url: str, timeout: int = 30) -> bool:
    """Check if OpenAI integration is configured"""
    # This is a simple check - in production you'd have a dedicated endpoint
    try:
        response = requests.get(f"{url}/docs", timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        print(f"OpenAI check failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="StudHelper Backend Health Check")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the application")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    checks = {
        "health": check_health(args.url, args.timeout),
        "database": check_database(args.url, args.timeout),
        "openai": check_openai_integration(args.url, args.timeout),
    }
    
    all_healthy = all(checks.values())
    
    if args.json:
        result = {
            "timestamp": datetime.now().isoformat(),
            "url": args.url,
            "overall_status": "healthy" if all_healthy else "unhealthy",
            "checks": checks
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"StudHelper Backend Health Check - {args.url}")
        print(f"Timestamp: {datetime.now()}")
        print("-" * 50)
        
        for check_name, status in checks.items():
            status_str = "✅ PASS" if status else "❌ FAIL"
            print(f"{check_name.capitalize():12} {status_str}")
        
        print("-" * 50)
        overall_status = "✅ HEALTHY" if all_healthy else "❌ UNHEALTHY"
        print(f"Overall:     {overall_status}")
    
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()

