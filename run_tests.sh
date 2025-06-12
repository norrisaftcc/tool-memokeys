#!/bin/bash
# Test runner for MemoKeys/KeyCast

echo "MemoKeys/KeyCast Test Suite"
echo "==========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install test requirements
echo "Installing test dependencies..."
pip install -q -r requirements-test.txt

echo ""
echo "Running tests..."
echo "----------------"

# Run pytest with coverage
pytest tests/ --cov=hotkey_panel_proto --cov-report=term-missing --cov-report=html

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi