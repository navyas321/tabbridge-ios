#!/usr/bin/env python3
"""Run every TabBridge test suite (relay + desktop host + integration).

Usage:  python run_tests.py
Exit code is non-zero if any suite fails.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SUITES = [
    ("relay/test_relay.py", "relay"),
    ("desktop/native-host/test_host.py", "desktop/native-host"),
    ("desktop/native-host/test_integration.py", "desktop/native-host"),
]


def main():
    failed = []
    for script, cwd in SUITES:
        print(f"\n=== {script} ===")
        r = subprocess.run([sys.executable, os.path.basename(script)],
                           cwd=os.path.join(ROOT, cwd))
        if r.returncode != 0:
            failed.append(script)
    print("\n" + "=" * 40)
    if failed:
        print(f"FAILED suites: {', '.join(failed)}")
        return 1
    print(f"All {len(SUITES)} suites passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
