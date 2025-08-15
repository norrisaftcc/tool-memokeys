# Hotkey Overlay - Quick Prototype

A lightweight Mac floating overlay that shows currently pressed hotkey combinations.

## What it does

- Shows a small floating window in the bottom-right corner
- Displays currently pressed modifier keys (⌘, ⇧, ⌥, ⌃) 
- Shows the full hotkey combination when you press keys
- Automatically shows descriptions for common shortcuts (e.g., "⌘ + V" shows "Paste")
- Auto-hides after 2 seconds of inactivity

## Quick Start

```bash
# Option 1: Use the run script
chmod +x run.sh
./run.sh

# Option 2: Run directly
chmod +x hotkey-overlay.swift
./hotkey-overlay.swift
```

## Important: Accessibility Permissions

⚠️ **First time setup:** macOS will ask for Accessibility permissions.

1. When you run the app, macOS will prompt you
2. Go to: System Preferences > Security & Privacy > Privacy > Accessibility
3. Add your Terminal app to the list and check the box
4. Restart the overlay

## Features

- **Floating window** - Always on top, visible on all spaces
- **Semi-transparent** - Won't block your view
- **Draggable** - Click and drag to reposition
- **Smart descriptions** - Recognizes common macOS shortcuts
- **Auto-hide** - Clears after 2 seconds

## Customization Ideas for Next Iteration

1. **Position**: Change the window position in `OverlayWindow.init()`
2. **Size**: Adjust `width` and `height` in the window rect
3. **Transparency**: Modify `withAlphaComponent(0.8)` 
4. **Font**: Change size/weight in `HotkeyView`
5. **Timeout**: Adjust the 2.0 second timer
6. **Add more shortcuts**: Expand the `getActionDescription` switch statement

## Technical Details

- Pure Swift, no dependencies
- Uses NSEvent global monitoring
- Runs as a simple script (no Xcode needed)
- ~200 lines of clean, readable code

## To Stop

Press `Ctrl+C` in the terminal window where it's running.

## Next Steps for Client Iteration

1. **Visual tweaks** - colors, fonts, position
2. **More shortcuts** - add app-specific combinations  
3. **Configuration** - JSON file for custom shortcuts
4. **Menu bar icon** - for easy access/quit
5. **Preferences window** - for customization

---

This is a rapid prototype to get something working immediately. Perfect for Scrum iteration!
