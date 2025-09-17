#!/usr/bin/env bash
set -euo pipefail

# Enforce conda env per rules
if [ "${CONDA_DEFAULT_ENV:-}" != "cmbagent" ]; then
  echo "[run_app] activate conda env: cmbagent" >&2
  # shellcheck disable=SC1090
  source ~/.bashrc >/dev/null 2>&1 || true
  conda activate cmbagent >/dev/null 2>&1 || true
fi

APP=/data/cmbagents/DenarioApp/src/denario_app/app.py
PORT_PRIMARY=8501
PORT_FALLBACK=8511

# Run smoke checks headlessly
echo "[run_app] running smoke checks"
/opt/miniforge/envs/cmbagent/bin/python /data/cmbagents/DenarioApp/smoke.py | sed -n '1,200p'

# Choose port: prefer 8501, else 8511
choose_port() {
  local p="$1"
  if ss -lnt | awk '{print $4}' | grep -q ":${p}$"; then
    return 1
  fi
  return 0
}

PORT=${PORT_PRIMARY}
if ! choose_port "$PORT_PRIMARY"; then
  echo "[run_app] port ${PORT_PRIMARY} busy, switching to ${PORT_FALLBACK}" >&2
  PORT=${PORT_FALLBACK}
fi

export DENARIOAPP_PORT=${PORT}

echo "[run_app] launching streamlit on port ${PORT}"
/opt/miniforge/envs/cmbagent/bin/python -m streamlit run "$APP" --server.port="${PORT}" --server.address=0.0.0.0 --server.headless true &
PID=$!
sleep 2

if ss -lnt | grep -q ":${PORT} "; then
  echo "[run_app] up: http://localhost:${PORT}"
else
  echo "[run_app] failed to start on port ${PORT}" >&2
  wait ${PID} || true
  exit 1
fi

wait ${PID}


