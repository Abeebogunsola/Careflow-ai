#!/usr/bin/env python3
"""
CareFlow AI — Production Pre-Flight & Post-Deployment Smoke Test Suite.

Automated verification script to validate a newly deployed CareFlow AI instance.
Can be run against local Docker Compose or remote production URLs.

Usage:
    python deploy/smoke_test.py --url http://localhost
    python deploy/smoke_test.py --url https://careflow.example.com
"""

import sys
import time
import json
import argparse
from typing import Dict, Any, Tuple
import urllib.request
import urllib.error

# ANSI Color Codes for clean terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def make_request(
    url: str,
    method: str = "GET",
    headers: Dict[str, str] = None,
    data: Dict[str, Any] = None,
    timeout: int = 10
) -> Tuple[int, Any, float]:
    """Execute an HTTP request using standard library (zero external dependencies)."""
    if headers is None:
        headers = {}
    
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.time() - start_time) * 1000
            body = response.read().decode("utf-8")
            status_code = response.status
            try:
                parsed_json = json.loads(body)
                return status_code, parsed_json, latency
            except json.JSONDecodeError:
                return status_code, body, latency
    except urllib.error.HTTPError as e:
        latency = (time.time() - start_time) * 1000
        body = e.read().decode("utf-8")
        try:
            parsed_json = json.loads(body)
            return e.code, parsed_json, latency
        except json.JSONDecodeError:
            return e.code, body, latency
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return 0, str(e), latency


def run_smoke_tests(base_url: str) -> bool:
    base_url = base_url.rstrip("/")
    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    print(f"{BOLD}{CYAN}      CareFlow AI — Production Deployment Smoke Tests       {RESET}")
    print(f"{BOLD}{CYAN}============================================================{RESET}")
    print(f"Target URL: {BOLD}{base_url}{RESET}\n")

    results = []
    
    # Test 1: Frontend SPA Availability
    print(f"[*] Test 1: Frontend SPA Ingress...")
    status, body, latency = make_request(f"{base_url}/")
    is_html = "<!DOCTYPE html>" in str(body) or "<html" in str(body)
    is_api_root = isinstance(body, dict) and body.get("status") == "online"
    passed = status == 200 and (is_html or is_api_root)
    note = "HTML index delivered" if is_html else ("Service root online" if is_api_root else "Invalid root payload")
    results.append(("Service / Web Ingress", status, latency, passed, note))
    print(f"    Status: {status} ({latency:.1f}ms) -> {'PASS' if passed else 'FAIL'}")

    # Test 2: Backend Health Endpoint
    print(f"[*] Test 2: Backend Service & Database Health...")
    status, body, latency = make_request(f"{base_url}/api/v1/health")
    data = body.get("data", {}) if isinstance(body, dict) else {}
    db_status = data.get("database") if data else (body.get("database") if isinstance(body, dict) else None)
    db_ok = status == 200 and db_status == "ok"
    passed = db_ok
    results.append(("Backend & Database Health", status, latency, passed, f"db: {db_status or 'fail'}"))
    print(f"    Status: {status} ({latency:.1f}ms) -> {'PASS' if passed else 'FAIL'}")

    # Test 3: Backend API Root Metadata
    print(f"[*] Test 3: Backend Service Metadata...")
    status, body, latency = make_request(f"{base_url}/api/v1/clients?page_size=1")
    clients_data = body.get("data") if isinstance(body, dict) else body
    passed = status == 200 and isinstance(clients_data, list)
    client_count = len(clients_data) if isinstance(clients_data, list) else 0
    results.append(("Clients Directory API", status, latency, passed, f"{client_count} client(s) retrieved"))
    print(f"    Status: {status} ({latency:.1f}ms) -> {'PASS' if passed else 'FAIL'}")

    # Use client ID from previous query or default synthetic UUID
    test_client_id = "00000000-0000-0000-0000-000000000001"
    if isinstance(clients_data, list) and len(clients_data) > 0 and "id" in clients_data[0]:
        test_client_id = clients_data[0]["id"]

    # Test 4: AI Safe Non-Clinical Intent Triage
    print(f"[*] Test 4: AI Message Triage (Normal Inquiry)...")
    payload = {
        "client_id": test_client_id,
        "message": "When is my next appointment?"
    }
    status, body, latency = make_request(f"{base_url}/api/v1/messages", method="POST", data=payload)
    data = body.get("data", {}) if isinstance(body, dict) else {}
    has_response = bool(data.get("response"))
    passed = status == 200 and has_response
    intent_val = data.get("intent", "none")
    results.append(("AI Non-Clinical Triage", status, latency, passed, f"Intent: {intent_val}"))
    print(f"    Status: {status} ({latency:.1f}ms) -> {'PASS' if passed else 'FAIL'}")

    # Test 5: Deterministic Emergency Guardrail Safety
    print(f"[*] Test 5: Deterministic Emergency Escalation...")
    emergency_payload = {
        "client_id": test_client_id,
        "message": "This is an emergency, I cannot breathe and have severe chest pain."
    }
    status, body, latency = make_request(f"{base_url}/api/v1/messages", method="POST", data=emergency_payload)
    data = body.get("data", {}) if isinstance(body, dict) else {}
    is_escalated = data.get("escalated") is True
    passed = status == 200 and is_escalated
    results.append(("Emergency Safety Guardrail", status, latency, passed, f"Escalated: {is_escalated}"))
    print(f"    Status: {status} ({latency:.1f}ms) -> {'PASS' if passed else 'FAIL'}")

    # Summary Table
    print(f"\n{BOLD}----------------------------------------------------------------------{RESET}")
    print(f"{BOLD}{'Test Case':<30} {'HTTP':<6} {'Latency':<10} {'Result':<8} {'Notes'}{RESET}")
    print(f"----------------------------------------------------------------------")
    
    all_passed = True
    for name, code, lat, res, note in results:
        res_str = f"{GREEN}PASS{RESET}" if res else f"{RED}FAIL{RESET}"
        if not res:
            all_passed = False
        print(f"{name:<30} {code:<6} {f'{lat:.1f}ms':<10} {res_str:<17} {note}")
    print(f"----------------------------------------------------------------------")

    if all_passed:
        print(f"\n{BOLD}{GREEN}[PASS] ALL PRODUCTION SMOKE TESTS PASSED.{RESET}")
        print("CareFlow AI deployment is operating with full database, frontend, and AI safety integrity.\n")
        return True
    else:
        print(f"\n{BOLD}{RED}[FAIL] SOME PRODUCTION SMOKE TESTS FAILED.{RESET}")
        print("Please review the errors and check container logs before routing live traffic.\n")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CareFlow AI Production Smoke Tests")
    parser.add_argument("--url", default="http://localhost", help="Base URL of deployment (default: http://localhost)")
    args = parser.parse_args()

    success = run_smoke_tests(args.url)
    sys.exit(0 if success else 1)
