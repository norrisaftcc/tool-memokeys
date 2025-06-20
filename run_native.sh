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
echo ""
echo "⚠️  IMPORTANT: Accessibility Permissions Required"
echo "================================================="
echo ""
echo "This app needs permission to monitor keyboard input to detect shortcuts."
echo ""
echo "When prompted:"
echo "1. Click 'Open System Preferences' in the dialog that appears"
echo "2. In System Preferences > Security & Privacy > Privacy > Accessibility:"
echo "   - Click the lock icon to make changes (enter your password)"
echo "   - Find 'Terminal' or 'Python' in the list"
echo "   - Check the checkbox next to it"
echo "   - Click the lock icon again to save"
echo ""
echo "If you don't see a prompt:"
echo "1. Open System Preferences > Security & Privacy > Privacy > Accessibility"
echo "2. Click the + button and add Terminal (or Python) from Applications/Utilities"
echo "3. Make sure it's checked"
echo ""
echo "Press Enter to continue..."
read -r

python hotkey_panel_proto/native_app.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ The app failed to start. This usually means:"
    echo "   - Accessibility permissions were not granted"
    echo "   - Python or Terminal needs to be added to Accessibility in System Preferences"
    echo ""
    echo "Please check System Preferences > Security & Privacy > Privacy > Accessibility"
    exit 1
fi