#!/usr/bin/env bash
set -euo pipefail

# DenarioApp Test Runner
# Runs smoke tests for retrieval paths and other components

echo "=== DenarioApp Test Suite ==="

# Ensure we're in the right environment
if [ "${CONDA_DEFAULT_ENV:-}" != "cmbagent" ]; then
  echo "[tests] activating conda env: cmbagent" >&2
  source ~/.bashrc >/dev/null 2>&1 || true
  conda activate cmbagent >/dev/null 2>&1 || true
fi

# Set up test environment
export PYTHONPATH="/data/cmbagents/DenarioApp/src:$PYTHONPATH"
export DENARIOAPP_STRICT_KEYS=0  # Don't require API keys for tests

# Test directories
TEST_DIR="/data/cmbagents/DenarioApp/tests"
TEMP_DIR="/tmp/denarioapp_tests"

# Create temp directory for tests
mkdir -p "$TEMP_DIR"

echo "[tests] Running preflight checks..."
python /data/cmbagents/DenarioApp/smoke.py >/dev/null 2>&1 || {
    echo "❌ Preflight checks failed"
    exit 1
}
echo "✅ Preflight checks passed"

echo "[tests] Running retrieval path tests..."
cd "$TEST_DIR"
python test_retrieval_paths.py || {
    echo "❌ Retrieval path tests failed"
    exit 1
}
echo "✅ Retrieval path tests passed"

echo "[tests] Running import tests..."
python -c "
import sys
sys.path.insert(0, '/data/cmbagents/DenarioApp/src')

# Test core imports
try:
    from denario_app import app, components, constants, preflight
    from denario_app.graphrag import get_graphrag_retriever
    from denario_app.arxiv_rag import get_arxiv_retriever
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

echo "[tests] Running component tests..."
python -c "
import sys
sys.path.insert(0, '/data/cmbagents/DenarioApp/src')

# Test component functions
try:
    from denario_app.components import _get_domain_context
    
    # Test domain context function
    context = _get_domain_context('Planck (web)')
    assert 'Planck' in context
    assert 'cosmological parameters' in context
    
    context = _get_domain_context('CAMB (web)')
    assert 'CAMB' in context
    assert 'Boltzmann solver' in context
    
    print('✅ Component functions working')
except Exception as e:
    print(f'❌ Component test failed: {e}')
    sys.exit(1)
"

echo "[tests] Running RAG provider tests..."
python -c "
import sys
sys.path.insert(0, '/data/cmbagents/DenarioApp/src')

# Test RAG providers
try:
    from denario_app.constants import RAG_PROVIDERS
    
    expected_providers = [
        'Perplexity (web)',
        'Domain (Planck/CAMB/CLASSY)',
        'GraphRAG (local corpus)',
        'arXiv (academic papers)'
    ]
    
    assert RAG_PROVIDERS == expected_providers, f'Expected {expected_providers}, got {RAG_PROVIDERS}'
    print('✅ RAG providers configured correctly')
except Exception as e:
    print(f'❌ RAG provider test failed: {e}')
    sys.exit(1)
"

echo "[tests] Running port policy tests..."
python -c "
import sys
sys.path.insert(0, '/data/cmbagents/DenarioApp/src')

# Test port policy
try:
    from denario_app.preflight import run_checks
    
    # Test with default port
    results = run_checks()
    assert 'network' in results
    assert 'port_free' in results['network']
    
    # Test port should be 8511 by default
    default_port = results['network']['port_free']['port']
    assert default_port == 8511, f'Expected port 8511, got {default_port}'
    
    print('✅ Port policy configured correctly')
except Exception as e:
    print(f'❌ Port policy test failed: {e}')
    sys.exit(1)
"

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 All tests passed successfully!"
echo ""
echo "Test Summary:"
echo "  ✅ Preflight checks"
echo "  ✅ Retrieval path tests"
echo "  ✅ Import tests"
echo "  ✅ Component tests"
echo "  ✅ RAG provider tests"
echo "  ✅ Port policy tests"
echo ""
echo "DenarioApp is ready for deployment!"

