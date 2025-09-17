# DenarioApp Docker Usage

## Overview
DenarioApp can be run in Docker with optional local Denario development support.

## Quick Start

### Using PyPI Denario (Default)
```bash
# Build and run the main app
docker-compose up --build

# Or run JupyterLab
docker-compose -f compose.jupyter.yaml up --build
```

### Using Local Denario Development Version
```bash
# Enable local Denario mount
export USE_LOCAL_DENARIO=1

# Uncomment the volume mount in compose.yaml:
# - /data/cmbagents/Denario:/denario:ro

# Build and run
docker-compose up --build
```

## Configuration

### Environment Variables
- `USE_LOCAL_DENARIO`: Set to `1` to use local Denario, `0` for PyPI (default: `0`)
- Standard DenarioApp environment variables (API keys, etc.)

### Volume Mounts
- `./project_app:/app/project_app` - Project data
- `./data:/app/data` - Additional data
- `./.env:/app/.env` - Environment configuration
- `/data/cmbagents/Denario:/denario:ro` - Local Denario source (optional)

## Services

### Main App (compose.yaml)
- **Port**: 8511 (host) → 8501 (container)
- **URL**: http://localhost:8511
- **Purpose**: Streamlit web interface

### JupyterLab (compose.jupyter.yaml)
- **Port**: 8512 (host) → 8888 (container)
- **URL**: http://localhost:8512
- **Purpose**: Interactive notebooks

## Entrypoint Script
The `entrypoint.sh` script handles:
1. Checking `USE_LOCAL_DENARIO` environment variable
2. Installing local Denario if mounted and enabled
3. Falling back to PyPI Denario if local not available
4. Verifying Denario installation
5. Executing the main command

## Troubleshooting

### Local Denario Not Found
```
[entrypoint] Local Denario mount not found, using PyPI version
```
**Solution**: Ensure the volume mount is uncommented in compose.yaml

### Denario Installation Failed
```
[entrypoint] WARNING: Failed to install local Denario, falling back to PyPI version
```
**Solution**: Check that the local Denario path is correct and accessible

### Port Conflicts
```bash
# Use different ports
docker-compose up --build -p 8513:8501
```

## Development Workflow

### With Local Denario
1. Make changes to `/data/cmbagents/Denario`
2. Set `USE_LOCAL_DENARIO=1`
3. Uncomment volume mount in compose.yaml
4. Run `docker-compose up --build`
5. Changes are reflected immediately

### Without Local Denario
1. Make changes to DenarioApp only
2. Run `docker-compose up --build`
3. Uses PyPI version of Denario

## File Structure
```
DenarioApp/
├── compose.yaml              # Main app compose
├── compose.jupyter.yaml      # JupyterLab compose
├── Dockerfile                # Main app Dockerfile
├── Dockerfile.jupyter        # JupyterLab Dockerfile
├── entrypoint.sh             # Entrypoint script
├── constraints.txt           # Dependency constraints
└── DOCKER_README.md          # This file
```
