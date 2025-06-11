#!/bin/bash
# MemoKeys Native App Launcher

echo "MemoKeys Native App Launcher"
echo "==========================="
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This native app currently only supports macOS"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -q -r requirements.txt
pip install -q -r hotkey_panel_proto/requirements.txt

# Run the native app
echo ""
echo "Starting MemoKeys Native App..."
echo "Note: You'll need to grant Accessibility permissions when prompted."
echo ""

python hotkey_panel_proto/native_app.py