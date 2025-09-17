# API Keys Configuration for DenarioApp

## Overview
DenarioApp requires API keys for various LLM providers and external services. This document explains how to configure and manage these keys securely.

## Required API Keys

### Core LLM Providers
- **OPENAI_API_KEY**: OpenAI API key for GPT models
- **ANTHROPIC_API_KEY**: Anthropic API key for Claude models  
- **GEMINI_API_KEY**: Google API key for Gemini models
- **PERPLEXITY_API_KEY**: Perplexity API key for web search

### Optional Keys
- **HUGGINGFACE_API_KEY**: For Hugging Face models (if used)
- **COHERE_API_KEY**: For Cohere models (if used)

## Configuration Methods

### Method 1: .env File (Recommended)
Create a `.env` file in the DenarioApp root directory:

```bash
# DenarioApp/.env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GEMINI_API_KEY=your-gemini-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here
```

### Method 2: Environment Variables
Set environment variables in your shell:

```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
export GEMINI_API_KEY="your-gemini-key-here"
export PERPLEXITY_API_KEY="pplx-your-perplexity-key-here"
```

### Method 3: System Environment
Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# Add to ~/.bashrc
echo 'export OPENAI_API_KEY="sk-your-openai-key-here"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"' >> ~/.bashrc
echo 'export GEMINI_API_KEY="your-gemini-key-here"' >> ~/.bashrc
echo 'export PERPLEXITY_API_KEY="pplx-your-perplexity-key-here"' >> ~/.bashrc
```

## Strict Mode Configuration

### DENARIOAPP_STRICT_KEYS Environment Variable
Control whether missing API keys cause the application to fail:

- **DENARIOAPP_STRICT_KEYS=0** (default): Missing keys show warnings but don't prevent startup
- **DENARIOAPP_STRICT_KEYS=1**: Missing keys cause preflight failure and prevent startup

### Setting Strict Mode
```bash
# Enable strict mode
export DENARIOAPP_STRICT_KEYS=1

# Disable strict mode (default)
export DENARIOAPP_STRICT_KEYS=0
```

### In .env File
```bash
# DenarioApp/.env
DENARIOAPP_STRICT_KEYS=1
OPENAI_API_KEY=sk-your-openai-key-here
# ... other keys
```

## Key Validation

### Preflight Checks
DenarioApp automatically validates API keys during startup:

```bash
# Run preflight checks
python /data/cmbagents/DenarioApp/smoke.py

# Check specific keys
python -c "
import os
from denario_app.preflight import run_checks
results = run_checks()
print('Missing keys:', results['keys']['missing'])
print('All keys present:', len(results['keys']['missing']) == 0)
"
```

### Manual Key Testing
Test individual keys:

```bash
# Test OpenAI key
python -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('OpenAI key valid:', client.models.list() is not None)
"

# Test Perplexity key
python -c "
import os
import requests
headers = {'Authorization': f'Bearer {os.getenv(\"PERPLEXITY_API_KEY\")}'}
response = requests.get('https://api.perplexity.ai/models', headers=headers)
print('Perplexity key valid:', response.status_code == 200)
"
```

## Security Best Practices

### 1. Never Commit Keys to Git
Ensure `.env` is in `.gitignore`:

```bash
# DenarioApp/.gitignore
.env
*.env
.env.local
.env.production
```

### 2. Use Environment-Specific Files
- `.env.local` - Local development
- `.env.production` - Production deployment
- `.env.staging` - Staging environment

### 3. Key Rotation
Regularly rotate API keys:

```bash
# Check key usage
python -c "
import os
from datetime import datetime
print(f'Keys last checked: {datetime.now()}')
for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'PERPLEXITY_API_KEY']:
    value = os.getenv(key)
    if value:
        print(f'{key}: Present (length: {len(value)})')
    else:
        print(f'{key}: Missing')
"
```

### 4. Docker Environment
For Docker deployments, use environment files:

```bash
# docker-compose.yaml
services:
  app:
    env_file:
      - .env
    environment:
      - DENARIOAPP_STRICT_KEYS=1
```

## Troubleshooting

### Common Issues

#### 1. Keys Not Loading
```bash
# Check if .env file exists and is readable
ls -la /data/cmbagents/DenarioApp/.env

# Check file permissions
chmod 600 /data/cmbagents/DenarioApp/.env
```

#### 2. Invalid Key Format
```bash
# Check key format
python -c "
import os
openai_key = os.getenv('OPENAI_API_KEY', '')
print('OpenAI key format valid:', openai_key.startswith('sk-'))
print('Key length:', len(openai_key))
"
```

#### 3. Network Issues
```bash
# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### Debug Mode
Enable debug logging for key issues:

```bash
export DENARIOAPP_DEBUG=1
python /data/cmbagents/DenarioApp/smoke.py
```

## Key Management Scripts

### Check All Keys
```bash
#!/bin/bash
# check_keys.sh
echo "=== API Key Status ==="
for key in OPENAI_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY PERPLEXITY_API_KEY; do
    if [ -n "${!key}" ]; then
        echo "✅ $key: Present"
    else
        echo "❌ $key: Missing"
    fi
done
```

### Generate .env Template
```bash
#!/bin/bash
# generate_env_template.sh
cat > .env.template << EOF
# DenarioApp API Keys Configuration
# Copy this file to .env and fill in your actual keys

# Core LLM Providers
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GEMINI_API_KEY=your-gemini-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here

# Optional Providers
HUGGINGFACE_API_KEY=your-huggingface-key-here
COHERE_API_KEY=your-cohere-key-here

# Configuration
DENARIOAPP_STRICT_KEYS=0
DENARIOAPP_DEBUG=0
EOF
echo "Created .env.template - copy to .env and fill in your keys"
```

## Integration with Preflight

The preflight system automatically checks for required keys:

```python
# From preflight.py
keys = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY", 
    "GEMINI_API_KEY",
    "PERPLEXITY_API_KEY",
]
missing_keys = [k for k in keys if not os.environ.get(k)]

# Strict mode enforcement
if os.environ.get("DENARIOAPP_STRICT_KEYS") == "1" and missing_keys:
    results["summary"]["errors"].append(
        f"missing required API keys: {missing_keys}"
    )
```

## Production Deployment

### Docker Secrets
For production, use Docker secrets:

```yaml
# docker-compose.prod.yaml
services:
  app:
    secrets:
      - openai_key
      - anthropic_key
      - gemini_key
      - perplexity_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_key
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_key
      - GEMINI_API_KEY_FILE=/run/secrets/gemini_key
      - PERPLEXITY_API_KEY_FILE=/run/secrets/perplexity_key

secrets:
  openai_key:
    file: ./secrets/openai_key.txt
  anthropic_key:
    file: ./secrets/anthropic_key.txt
  gemini_key:
    file: ./secrets/gemini_key.txt
  perplexity_key:
    file: ./secrets/perplexity_key.txt
```

### Kubernetes Secrets
```yaml
# k8s-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: denarioapp-keys
type: Opaque
data:
  openai-key: <base64-encoded-key>
  anthropic-key: <base64-encoded-key>
  gemini-key: <base64-encoded-key>
  perplexity-key: <base64-encoded-key>
```

## Summary

- **Required Keys**: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, PERPLEXITY_API_KEY
- **Configuration**: Use `.env` file or environment variables
- **Strict Mode**: Set `DENARIOAPP_STRICT_KEYS=1` to require all keys
- **Security**: Never commit keys to git, use proper file permissions
- **Validation**: Use preflight checks to verify key configuration
- **Production**: Use Docker secrets or Kubernetes secrets for secure deployment

