#!/bin/bash
# KeyCast - Live Hotkey Display

echo "KeyCast - Live Keyboard Monitor"
echo "==============================="
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: KeyCast native app currently only supports macOS"
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

# Run KeyCast
echo ""
echo "Starting KeyCast..."
echo ""
echo "⚠️  IMPORTANT: Accessibility Permissions Required"
echo "================================================="
echo ""
echo "KeyCast displays the keys you're currently pressing in real-time."
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

python hotkey_panel_proto/hotkey_display.py "$@"

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ KeyCast failed to start. This usually means:"
    echo "   - Accessibility permissions were not granted"
    echo "   - Python or Terminal needs to be added to Accessibility in System Preferences"
    echo ""
    echo "Please check System Preferences > Security & Privacy > Privacy > Accessibility"
    exit 1
fi