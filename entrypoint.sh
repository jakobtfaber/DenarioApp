#!/usr/bin/env bash
set -euo pipefail

# DenarioApp Docker Entrypoint Script
# Handles optional local Denario installation and starts the application

echo "[entrypoint] Starting DenarioApp entrypoint..."

# Check if we should use local Denario
USE_LOCAL_DENARIO=${USE_LOCAL_DENARIO:-0}

if [ "$USE_LOCAL_DENARIO" = "1" ]; then
    echo "[entrypoint] USE_LOCAL_DENARIO=1, checking for local Denario mount..."
    
    # Check if local Denario is mounted
    if [ -d "/denario" ] || [ -d "/home/user/denario" ]; then
        DENARIO_PATH=""
        if [ -d "/denario" ]; then
            DENARIO_PATH="/denario"
        elif [ -d "/home/user/denario" ]; then
            DENARIO_PATH="/home/user/denario"
        fi
        
        if [ -n "$DENARIO_PATH" ]; then
            echo "[entrypoint] Found local Denario at $DENARIO_PATH, installing in editable mode..."
            pip install -e "$DENARIO_PATH" || {
                echo "[entrypoint] WARNING: Failed to install local Denario, falling back to PyPI version"
                echo "[entrypoint] Installing Denario from PyPI..."
                pip install denario
            }
        else
            echo "[entrypoint] Local Denario mount not found, using PyPI version"
            pip install denario
        fi
    else
        echo "[entrypoint] Local Denario mount not found, using PyPI version"
        pip install denario
    fi
else
    echo "[entrypoint] USE_LOCAL_DENARIO=0, using PyPI version of Denario"
    pip install denario
fi

# Verify Denario installation
echo "[entrypoint] Verifying Denario installation..."
python -c "import denario; print(f'Denario version: {denario.__version__ if hasattr(denario, \"__version__\") else \"unknown\"}')" || {
    echo "[entrypoint] ERROR: Failed to import Denario"
    exit 1
}

echo "[entrypoint] DenarioApp setup complete, executing command: $*"

# Execute the original command
exec "$@"
