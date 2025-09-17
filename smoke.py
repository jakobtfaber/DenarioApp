#!/usr/bin/env python3
import os
import sys
import json
import socket
import time


def tcp_check(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main() -> int:
    # Make src importable when run from repo root
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "src")
    if src not in sys.path:
        sys.path.insert(0, src)

    # Import preflight
    try:
        from denario_app.preflight import run_checks  # type: ignore
    except Exception as e:
        print(json.dumps({"summary": {"ok": False, "errors": [
              f"preflight import failed: {e}"]}}, indent=2))
        return 1

    results = run_checks()

    # Optional health check
    port = int(os.environ.get("DENARIOAPP_PORT", "8511"))
    if tcp_check("127.0.0.1", port):
        results.setdefault("network", {})["ui_health_tcp"] = {
            "port": port, "ok": True}
    else:
        results.setdefault("network", {})["ui_health_tcp"] = {
            "port": port, "ok": False}

    print(json.dumps(results, indent=2))
    return 0 if results["summary"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
