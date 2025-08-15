# CLAUDE.md - Hotkey Overlay Prototype Status

## What Was Built
Created a standalone Swift-based floating overlay for macOS that displays currently pressed hotkey combinations in real-time.

## Location
`/Users/norrisa/Documents/dev/github/tool-memokeys-overlay/`

**Note:** This is a SEPARATE folder from the main tool-memokeys repo to avoid conflicts with other development.

## Files Created
- `hotkey-overlay.swift` - Main Swift script (executable, ~200 lines)
- `run.sh` - Bash launcher with instructions
- `README.md` - Documentation and customization guide

## How It Works
- Pure Swift script with shebang (`#!/usr/bin/swift`) - runs directly without compilation
- Uses `NSEvent.addGlobalMonitorForEvents` for system-wide keyboard monitoring
- Creates floating `NSWindow` with `NSTextField` for display
- Shows modifier keys (⌘, ⇧, ⌥, ⌃) + key combinations
- Includes descriptions for common shortcuts (e.g., "⌘ + V" → "Paste")
- Auto-hides after 2 seconds of inactivity

## Current Features
- Floating black semi-transparent window (bottom-right corner)
- Draggable window
- Real-time hotkey display
- Built-in descriptions for ~25 common macOS shortcuts
- No build process needed - direct execution

## To Run
```bash
cd /Users/norrisa/Documents/dev/github/tool-memokeys-overlay
chmod +x run.sh
./run.sh
# Stop with Ctrl+C
```

## Important Notes
1. **Accessibility Permissions Required**: First run will prompt for permissions
   - System Preferences > Security & Privacy > Privacy > Accessibility
   - Add Terminal to the list

2. **Approach Rationale**: 
   - Chose Swift script over compiled app for rapid iteration
   - No Xcode, no build step, no dependencies
   - Client can modify and test immediately
   - Similar to bash/python scripts but with native macOS API access

## Next Iteration Opportunities
1. Visual customization (position, size, colors, transparency)
2. Expanded shortcut dictionary
3. App-specific shortcut detection
4. Configuration file support (JSON/plist)
5. Menu bar integration
6. Preferences window

## Technical Stack
- Language: Swift (script mode)
- APIs: Cocoa (NSWindow, NSEvent, NSTextField)
- No external dependencies
- Runs on any Mac with Swift runtime (built-in on modern macOS)

## Client Benefit
- Immediate working prototype
- Zero setup complexity
- Edit-and-run workflow for quick iterations
- Foundation for more sophisticated features

---

*This is a rapid prototype focused on getting something functional to the client ASAP for Scrum-style iteration.*
