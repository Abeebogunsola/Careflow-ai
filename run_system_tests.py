"""
Unified System-Wide Test Runner and Quality Verification Suite for CareFlow AI.

Executes comprehensive verification across all 13 testing dimensions:
1. Backend Unit & Business Logic Tests
2. Integration & Database Cascade Tests
3. End-to-End (E2E) Longitudinal Scenario Tests
4. REST API Contract & Input Boundary Validation
5. Database Migration & Integrity Checks
6. AI Agent Behavior, Hallucination Resistance & Safety Filters
7. n8n Automation Workflow Schemas & Idempotency Rules
8. Analytics Extraction, Star Schema Views & DAX Metric Parity
9. Privacy & Strict Zero-PII Leak Scanning
10. Security Configuration & Secret Scans
11. Error Handling & Structured Payload Formatting
12. Full Regression Suite (Zero failures)
13. Production Readiness & Frontend Build Validation
"""

import os
import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
VENV_PYTEST = ROOT_DIR / ".venv" / "Scripts" / "pytest.exe"
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"

# Fallback for non-Windows environments
if not VENV_PYTEST.exists():
    VENV_PYTEST = Path("pytest")
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)


def run_step(title: str, command: list, cwd: Path) -> tuple:
    """Runs a shell command, measures duration, and returns (success, output, elapsed)."""
    print(f"\n================================================================================")
    print(f">> [RUNNING] {title}")
    print(f"   Command: {' '.join(str(c) for c in command)}")
    print(f"   Directory: {cwd}")
    print(f"================================================================================")

    start = time.time()
    result = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        shell=True,
    )
    elapsed = time.time() - start
    success = result.returncode == 0

    if success:
        print(f">> [PASSED] {title} ({elapsed:.2f}s)")
    else:
        print(f">> [FAILED] {title} ({elapsed:.2f}s) - Exit code: {result.returncode}")
        print(result.stdout)
        print(result.stderr)

    return success, result.stdout + "\n" + result.stderr, elapsed


def main():
    print("=" * 80)
    print("       CareFlow AI - System-Wide Automated Quality Verification Suite")
    print("=" * 80)

    results = []

    # 1. Backend Pytest Suite (Unit, Integration, E2E, AI, Workflows, Security, Analytics)
    b_success, b_out, b_time = run_step(
        "Backend Full Pytest Suite (160 Tests)",
        [str(VENV_PYTEST), "-v"],
        cwd=BACKEND_DIR,
    )
    results.append(("Backend Test Suite (Unit, Integration, E2E, AI, Security)", b_success, f"{b_time:.2f}s"))

    # 2. Frontend Vitest Suite (Components, Shell, Feature Views)
    f_success, f_out, f_time = run_step(
        "Frontend Vitest Suite (20 Tests)",
        ["npm", "test", "--", "--run"],
        cwd=FRONTEND_DIR,
    )
    results.append(("Frontend Test Suite (Shell, Components, 8 Feature Views)", f_success, f"{f_time:.2f}s"))

    # 3. Frontend Production Build & TypeScript Check
    build_success, build_out, build_time = run_step(
        "Frontend Production Bundle Build (tsc + vite build)",
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
    )
    results.append(("Frontend Production Build & TS Compilation", build_success, f"{build_time:.2f}s"))

    # 4. Analytics Data Extraction Pipeline
    analytics_success, analytics_out, analytics_time = run_step(
        "Analytics Star Schema ETL Extraction (export_data.py)",
        [str(VENV_PYTHON), "analytics/export_data.py"],
        cwd=ROOT_DIR,
    )
    results.append(("Analytics Extraction Pipeline & CSV Generation", analytics_success, f"{analytics_time:.2f}s"))

    # Print Summary Matrix
    print("\n" + "=" * 80)
    print("                 SYSTEM VERIFICATION MATRIX & AUDIT REPORT")
    print("=" * 80)
    print(f"{'Verification Area':<58} | {'Status':<8} | {'Duration'}")
    print("-" * 80)

    all_passed = True
    for area, passed, dur in results:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"{area:<58} | {status_str:<8} | {dur}")

    print("-" * 80)
    overall_status = "ALL TESTS PASSED (100%) - SYSTEM READY" if all_passed else "VERIFICATION FAILED"
    print(f"Overall Result: {overall_status}")
    print("=" * 80)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
