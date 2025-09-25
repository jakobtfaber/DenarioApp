import os
import sys
import json
import socket
import importlib.util
from typing import Dict, Any, List
from urllib.request import urlopen
from urllib.error import URLError
import subprocess


def _load_env_file(path: str) -> None:
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # do not overwrite explicitly set env vars
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        # best-effort; do not fail preflight if .env parsing has issues
        pass


def check_module(name: str) -> str:
    return "ok" if importlib.util.find_spec(name) is not None else "missing"


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0


def ui_health_ok(port: int, timeout_sec: float = 1.0) -> bool:
    try:
        with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8", errors="ignore").strip()
            return resp.status == 200 and body == "ok"
    except Exception:
        return False


def run_checks() -> Dict[str, Any]:
    # Best-effort: auto-load DenarioApp/.env if present to help preflight find
    # keys
    app_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..'))
    _load_env_file(os.path.join(app_root, '.env'))

    # Check if we're using the cmbagent environment (either via
    # CONDA_DEFAULT_ENV or interpreter path)
    conda_env = os.environ.get("CONDA_DEFAULT_ENV", "")
    interpreter_path = sys.executable
    is_cmbagent_env = (conda_env == "cmbagent" or
                       "/opt/miniforge/envs/cmbagent/bin/python" in interpreter_path)

    results: Dict[str, Any] = {
        "env": {
            "CONDA_DEFAULT_ENV": conda_env,
            "interpreter_path": interpreter_path,
            "ok": is_cmbagent_env,
        },
        "modules": {
            "streamlit": check_module("streamlit"),
            "denario": check_module("denario"),
            "streamlit_pdf_viewer": check_module("streamlit_pdf_viewer"),
            "PIL": check_module("PIL"),
        },
        "imports": {},
        "network": {},
        "matlab": {},
        "summary": {"errors": []},
    }

    # Import details when present
    if results["modules"]["denario"] == "ok":
        try:
            import denario  # type: ignore
            results["imports"]["denario_path"] = getattr(
                denario, "__file__", "?")
        except Exception as e:  # pragma: no cover
            results["imports"]["denario_error"] = str(e)
            results["summary"]["errors"].append(f"denario import failed: {e}")

    if results["modules"]["streamlit"] == "ok":
        try:
            import streamlit  # noqa: F401  # type: ignore
        except Exception as e:  # pragma: no cover
            results["imports"]["streamlit_error"] = str(e)
            results["summary"]["errors"].append(
                f"streamlit import failed: {e}")

    # Ensure Streamlit port is free by default (canonical 8501)
    default_port = int(os.environ.get("DENARIOAPP_PORT", "8501"))
    free = port_free(default_port)
    results["network"]["port_free"] = {"port": default_port, "free": free}
    if not free:
        results["summary"]["errors"].append(
            f"port {default_port} is already in use")

    # If default port is busy, consider alternate known ports and pass if any
    # UI is healthy
    candidate_ports: List[int] = [default_port]
    if default_port != 8511:
        candidate_ports.append(8511)
    healthy_port: int = -1
    for p in candidate_ports:
        if not port_free(p) and ui_health_ok(p):
            healthy_port = p
            break
    if healthy_port != -1:
        results["network"]["ui_health_tcp"] = {
            "port": healthy_port, "ok": True}
        # Remove port-in-use error if present, since a healthy UI is already
        # running
        try:
            results["summary"]["errors"].remove(
                f"port {default_port} is already in use")
        except ValueError:
            pass

    # Basic keys presence (warn-only unless user enables strict)
    keys: List[str] = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "PERPLEXITY_API_KEY",
    ]
    missing_keys = [k for k in keys if not os.environ.get(k)]
    results["keys"] = {"required_checked": keys, "missing": missing_keys}

    # Summarize errors
    if not results["env"]["ok"]:
        results["summary"]["errors"].append(
            "Not in required conda env: cmbagent (set CONDA_DEFAULT_ENV=cmbagent)"
        )
    for mod, status in results["modules"].items():
        if status != "ok":
            results["summary"]["errors"].append(f"missing module: {mod}")

    # MATLAB docker probe (optional)
    try:
        results["matlab"] = _probe_matlab_docker()
    except Exception:  # pragma: no cover
        results["matlab"] = {"enabled": False}

    # Optional strict mode to enforce keys as errors
    if os.environ.get(
            "DENARIOAPP_STRICT_KEYS") == "1" and results["keys"]["missing"]:
        results["summary"]["errors"].append(
            f"missing required API keys: {results['keys']['missing']}"
        )

    results["summary"]["ok"] = len(results["summary"]["errors"]) == 0
    return results


def _probe_matlab_docker() -> Dict[str, Any]:
    """Probe MATLAB docker container and installed toolboxes.

    Non-fatal: returns dict with status and any info gathered.
    """
    info: Dict[str, Any] = {"ok": False}
    container = os.environ.get("MATLAB_DOCKER_CONTAINER", "matlab_r2025a")
    backend = os.environ.get("MATLAB_BACKEND", "")
    if backend != "docker":
        return {"enabled": False}

    info["enabled"] = True
    info["container"] = container

    # Quick container liveness check
    try:
        ps = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
        )
        names = ps.stdout.strip().splitlines()
        info["running"] = container in names
        if not info["running"]:
            return info
    except Exception:
        info["error"] = "docker not available"
        return info

    # Prefer single JSON report from capability_report.m
    try:
        rep = subprocess.run([
            'docker','exec',container,'matlab','-batch','capability_report'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        if rep.returncode == 0 and rep.stdout.strip().startswith('{'):
            info['capabilities'] = json.loads(rep.stdout.strip())
            info['ok'] = True
            return info
        else:
            info['stderr'] = rep.stderr.strip()
    except Exception as e:
        info['error'] = str(e)
    info['ok'] = True

    return info


def main() -> None:
    as_json = "--json" in sys.argv
    results = run_checks()
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"env: {results['env']}")
        print(f"modules: {results['modules']}")
        print(f"imports: {results['imports']}")
        print(f"network: {results['network']}")
        if results["keys"]["missing"]:
            print(f"warn: missing keys: {results['keys']['missing']}")
        if results["summary"]["errors"]:
            print("errors:")
            for e in results["summary"]["errors"]:
                print(f" - {e}")
    # non-zero exit if not ok
    sys.exit(0 if results["summary"]["ok"] else 1)


if __name__ == "__main__":
    main()
