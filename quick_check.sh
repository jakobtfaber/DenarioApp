#!/usr/bin/env bash
# One-line health check for DenarioApp
# Usage: bash /data/cmbagents/DenarioApp/quick_check.sh

conda activate cmbagent >/dev/null 2>&1 && python /data/cmbagents/DenarioApp/smoke.py >/dev/null 2>&1 && echo "✅ DenarioApp ready" || echo "❌ DenarioApp not ready"

