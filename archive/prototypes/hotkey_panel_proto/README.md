# Hotkey Panel Prototype

A native macOS application for practicing keyboard shortcuts with real-time detection.

## Features
- Direct keyboard shortcut interception (no browser limitations)
- Native macOS UI using PyObjC
- Immediate visual feedback
- Score tracking and results display

## Requirements
- macOS (tested on 10.15+)
- Python 3.8+
- Accessibility permissions

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
# From project root
./run_native.sh

# Or directly
python hotkey_panel_proto/native_app.py
```

## Accessibility Permissions
On first run, macOS will prompt you to grant Accessibility permissions:
1. System Preferences → Security & Privacy → Privacy
2. Select "Accessibility" from the left panel
3. Add Terminal (or your Python app) to the allowed list

## Architecture
- `native_app.py` - Main application with:
  - `ShortcutManager` - Loads shortcuts from JSON files
  - `KeyboardMonitor` - Captures keyboard events using pynput
  - `MemoKeysApp` - Native macOS UI and game logic

## Known Limitations
- macOS only (can be extended to other platforms)
- Requires Accessibility permissions
- Limited to 5 shortcuts in MVP mode