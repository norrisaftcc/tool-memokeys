#!/usr/bin/env python3
"""
MemoKeys Hotkey Display - Live keyboard shortcut viewer
Shows currently pressed keys in real-time
"""

import sys
import threading
import json
import argparse
from pathlib import Path
from collections import OrderedDict

# Platform-specific imports
if sys.platform == "darwin":  # macOS
    from pynput import keyboard
    from AppKit import (
        NSApplication,
        NSApp,
        NSWindow,
        NSView,
        NSTextField,
        NSButton,
        NSMakeRect,
        NSFont,
        NSColor,
        NSTimer,
        NSApplicationActivationPolicyRegular,
        NSTextAlignmentCenter,
        NSBackingStoreBuffered,
    )
    import objc
else:
    print("This native app currently only supports macOS")
    sys.exit(1)


class KeyboardMonitor:
    """Monitors keyboard input and reports current state"""

    def __init__(self, callback):
        self.callback = callback
        self.current_keys = OrderedDict()  # Maintains order of key presses
        self.listener = None
        self.use_icons = True  # Can be updated by the app

    def start(self):
        """Start monitoring keyboard"""
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press, on_release=self._on_release
            )
            self.listener.start()
        except Exception as e:
            print(f"\n❌ Failed to start keyboard monitoring: {e}")
            print(
                "\nThis usually means Accessibility permissions haven't been granted."
            )
            print(
                "Please check System Preferences > Security & Privacy > Privacy > Accessibility"
            )
            print("and ensure Terminal or Python is listed and checked.")
            raise

    def stop(self):
        """Stop monitoring keyboard"""
        if self.listener:
            self.listener.stop()

    def _get_key_name(self, key):
        """Get a readable name for the key"""
        if hasattr(key, "char") and key.char:
            return key.char.upper()
        elif hasattr(key, "name"):
            name = key.name.lower()

            # Choose icon or text based on current mode
            if self.use_icons:
                key_map = {
                    "cmd": "⌘",
                    "command": "⌘",
                    "ctrl": "⌃",
                    "control": "⌃",
                    "alt": "⌥",
                    "option": "⌥",
                    "shift": "⇧",
                    "return": "↩",
                    "enter": "↩",
                    "space": "␣",
                    "tab": "⇥",
                    "escape": "⎋",
                    "esc": "⎋",
                    "backspace": "⌫",
                    "delete": "⌦",
                    "up": "↑",
                    "down": "↓",
                    "left": "←",
                    "right": "→",
                    "caps_lock": "⇪",
                    "f1": "F1",
                    "f2": "F2",
                    "f3": "F3",
                    "f4": "F4",
                    "f5": "F5",
                    "f6": "F6",
                    "f7": "F7",
                    "f8": "F8",
                    "f9": "F9",
                    "f10": "F10",
                    "f11": "F11",
                    "f12": "F12",
                }
            else:
                key_map = {
                    "cmd": "CMD",
                    "command": "CMD",
                    "ctrl": "CTRL",
                    "control": "CTRL",
                    "alt": "ALT",
                    "option": "ALT",
                    "shift": "SHIFT",
                    "return": "ENTER",
                    "enter": "ENTER",
                    "space": "SPACE",
                    "tab": "TAB",
                    "escape": "ESC",
                    "esc": "ESC",
                    "backspace": "BACKSPACE",
                    "delete": "DELETE",
                    "up": "UP",
                    "down": "DOWN",
                    "left": "LEFT",
                    "right": "RIGHT",
                    "caps_lock": "CAPS",
                    "f1": "F1",
                    "f2": "F2",
                    "f3": "F3",
                    "f4": "F4",
                    "f5": "F5",
                    "f6": "F6",
                    "f7": "F7",
                    "f8": "F8",
                    "f9": "F9",
                    "f10": "F10",
                    "f11": "F11",
                    "f12": "F12",
                }
            return key_map.get(name, name.upper())
        else:
            # Try to extract readable name from string representation
            key_str = str(key).lower().replace("key.", "")
            return key_str.upper()

    def _should_display_key(self, key_name):
        """Check if key should be displayed (filter out single letters)"""
        # Don't display single letters (a-z) unless they're part of a combo
        if len(key_name) == 1 and key_name.lower() in "abcdefghijklmnopqrstuvwxyz":
            # Only show if we have modifiers (check both icon and text versions)
            modifiers = {"⌘", "⌃", "⌥", "⇧", "CMD", "CTRL", "ALT", "SHIFT"}
            has_modifiers = any(mod in self.current_keys for mod in modifiers)
            return has_modifiers
        return True

    def _on_press(self, key):
        """Handle key press"""
        try:
            key_name = self._get_key_name(key)

            # Store with timestamp to maintain order
            if key_name not in self.current_keys:
                self.current_keys[key_name] = True

            # Filter keys before sending to callback
            display_keys = [
                k for k in self.current_keys.keys() if self._should_display_key(k)
            ]

            # Only notify if there are keys to display
            if display_keys:
                self.callback(display_keys)
            else:
                self.callback([])

        except Exception as e:
            print(f"Error in key press handler: {e}")

    def _on_release(self, key):
        """Handle key release"""
        try:
            key_name = self._get_key_name(key)

            # Remove from current keys
            if key_name in self.current_keys:
                del self.current_keys[key_name]

            # Filter keys before sending to callback
            display_keys = [
                k for k in self.current_keys.keys() if self._should_display_key(k)
            ]

            # Always notify callback with current state
            self.callback(display_keys)

        except Exception as e:
            print(f"Error in key release handler: {e}")


class ShortcutLookup:
    """Handles loading and looking up shortcut descriptions"""

    def __init__(self, mode=None):
        self.shortcuts = {}
        self.mode = mode
        self.shortcuts_dir = Path(__file__).parent.parent / "data" / "shortcuts"
        self.load_shortcuts()

    def get_available_modes(self):
        """Get list of available modes"""
        modes_file = self.shortcuts_dir / "modes.json"
        try:
            with open(modes_file, "r") as f:
                data = json.load(f)
                return data.get("modes", {})
        except Exception as e:
            print(f"Error loading modes: {e}")
            return {}

    def load_shortcuts(self):
        """Load shortcuts based on mode or all files"""
        if self.mode:
            self.load_mode_shortcuts()
        else:
            self.load_all_shortcuts()

    def load_mode_shortcuts(self):
        """Load shortcuts for a specific mode"""
        modes = self.get_available_modes()
        if self.mode not in modes:
            print(f"Mode '{self.mode}' not found. Available modes: {list(modes.keys())}")
            return

        mode_config = modes[self.mode]
        print(f"Loading mode: {mode_config['name']} - {mode_config['description']}")
        
        for file_path in mode_config["files"]:
            full_path = self.shortcuts_dir / file_path
            self.load_shortcuts_from_file(full_path)

    def load_all_shortcuts(self):
        """Load all shortcut JSON files (excluding modes.json)"""
        for json_file in self.shortcuts_dir.rglob("*.json"):
            if json_file.name != "modes.json":
                self.load_shortcuts_from_file(json_file)

    def load_shortcuts_from_file(self, json_file):
        """Load shortcuts from a specific file"""
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                if "shortcuts" in data:
                    for shortcut in data["shortcuts"]:
                        if "mac" in shortcut and "action" in shortcut:
                            # Normalize the key combination for lookup
                            key_combo = self.normalize_shortcut(shortcut["mac"])
                            self.shortcuts[key_combo] = shortcut["action"]
        except Exception as e:
            print(f"Error loading shortcuts from {json_file}: {e}")

    def normalize_shortcut(self, shortcut_str):
        """Normalize shortcut string for consistent lookup"""
        # Convert to lowercase and standardize modifier names
        normalized = shortcut_str.lower()
        normalized = normalized.replace("command", "cmd")
        normalized = normalized.replace("option", "alt")
        normalized = normalized.replace("control", "ctrl")
        normalized = normalized.replace(" ", "")

        # Split by + and sort modifiers
        parts = normalized.split("+")
        modifiers = []
        main_key = ""

        for part in parts:
            if part in ["cmd", "ctrl", "alt", "shift"]:
                modifiers.append(part)
            else:
                main_key = part

        modifiers.sort()
        return "+".join(modifiers + [main_key])

    def lookup(self, key_combination):
        """Look up description for a key combination"""
        # Try different normalization approaches
        normalized = self.normalize_shortcut(key_combination)

        # Also try with icon-to-text conversion
        icon_to_text = {"⌘": "cmd", "⌃": "ctrl", "⌥": "alt", "⇧": "shift"}

        text_combo = key_combination
        for icon, text in icon_to_text.items():
            text_combo = text_combo.replace(icon, text)

        normalized_text = self.normalize_shortcut(text_combo)

        return self.shortcuts.get(normalized) or self.shortcuts.get(normalized_text)


class HotkeyDisplayApp:
    """Main application showing live hotkey display"""

    def __init__(self, use_icons=True, mode=None):
        self.keyboard_monitor = None
        self.use_icons = use_icons  # Toggle between icons (⌘) and text (CMD)
        self.mode = mode
        self.shortcut_lookup = ShortcutLookup(mode=mode)

        # UI elements
        self.window = None
        self.keys_label = None
        self.description_label = None
        self.instruction_label = None
        self.quit_button = None
        self.toggle_button = None

    def setup_ui(self):
        """Create the native macOS UI"""
        # Create application
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        # Create window
        frame = NSMakeRect(100, 100, 500, 400)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            15,  # Titled | Closable | Miniaturizable | Resizable
            NSBackingStoreBuffered,
            False,
        )
        title = "KeyCast - Live Hotkey Display"
        if self.mode:
            modes = self.shortcut_lookup.get_available_modes()
            if self.mode in modes:
                mode_name = modes[self.mode]["name"]
                title = f"KeyCast - {mode_name} Mode"
        self.window.setTitle_(title)

        # Make window stay on top
        self.window.setLevel_(3)  # Floating window level

        # Create content view
        content_view = NSView.alloc().initWithFrame_(frame)

        # Title label
        title_frame = NSMakeRect(20, 340, 460, 40)
        title_label = NSTextField.alloc().initWithFrame_(title_frame)
        title_label.setStringValue_("KeyCast")
        title_label.setBezeled_(False)
        title_label.setDrawsBackground_(False)
        title_label.setEditable_(False)
        title_label.setFont_(NSFont.boldSystemFontOfSize_(24))
        title_label.setAlignment_(NSTextAlignmentCenter)
        content_view.addSubview_(title_label)

        # Keys display label - large area for showing current keys
        keys_frame = NSMakeRect(20, 210, 460, 80)
        self.keys_label = NSTextField.alloc().initWithFrame_(keys_frame)
        self.keys_label.setStringValue_("Press any keys...")
        self.keys_label.setBezeled_(True)
        self.keys_label.setDrawsBackground_(True)
        self.keys_label.setEditable_(False)
        self.keys_label.setFont_(NSFont.systemFontOfSize_(32))
        self.keys_label.setAlignment_(NSTextAlignmentCenter)

        # Set background color
        self.keys_label.setBackgroundColor_(NSColor.controlBackgroundColor())
        content_view.addSubview_(self.keys_label)

        # Description label - shows what the shortcut does
        description_frame = NSMakeRect(20, 150, 460, 50)
        self.description_label = NSTextField.alloc().initWithFrame_(description_frame)
        self.description_label.setStringValue_("")
        self.description_label.setBezeled_(False)
        self.description_label.setDrawsBackground_(False)
        self.description_label.setEditable_(False)
        self.description_label.setFont_(NSFont.systemFontOfSize_(16))
        self.description_label.setAlignment_(NSTextAlignmentCenter)
        self.description_label.setTextColor_(NSColor.systemBlueColor())
        content_view.addSubview_(self.description_label)

        # Instruction label
        instruction_frame = NSMakeRect(20, 90, 460, 40)
        self.instruction_label = NSTextField.alloc().initWithFrame_(instruction_frame)
        self.instruction_label.setStringValue_(
            "Hold down any key combination to see it displayed above"
        )
        self.instruction_label.setBezeled_(False)
        self.instruction_label.setDrawsBackground_(False)
        self.instruction_label.setEditable_(False)
        self.instruction_label.setFont_(NSFont.systemFontOfSize_(14))
        self.instruction_label.setAlignment_(NSTextAlignmentCenter)
        self.instruction_label.setTextColor_(NSColor.secondaryLabelColor())
        content_view.addSubview_(self.instruction_label)

        # Toggle button (Icons/Text)
        toggle_frame = NSMakeRect(100, 20, 100, 30)
        self.toggle_button = NSButton.alloc().initWithFrame_(toggle_frame)
        button_text = "Use Text" if self.use_icons else "Use Icons"
        self.toggle_button.setTitle_(button_text)
        self.toggle_button.setButtonType_(0)  # Momentary push button
        self.toggle_button.setBezelStyle_(1)  # Rounded rect
        self.toggle_button.setTarget_(self)
        self.toggle_button.setAction_("toggleDisplayMode:")
        content_view.addSubview_(self.toggle_button)

        # Quit button
        quit_frame = NSMakeRect(300, 20, 100, 30)
        self.quit_button = NSButton.alloc().initWithFrame_(quit_frame)
        self.quit_button.setTitle_("Quit")
        self.quit_button.setButtonType_(0)  # Momentary push button
        self.quit_button.setBezelStyle_(1)  # Rounded rect
        self.quit_button.setTarget_(self)
        self.quit_button.setAction_("quitApp:")
        content_view.addSubview_(self.quit_button)

        # Set content view
        self.window.setContentView_(content_view)

        # Show window
        self.window.makeKeyAndOrderFront_(None)

        return app

    @objc.IBAction
    def toggleDisplayMode_(self, sender):
        """Toggle between icon and text display modes"""
        print("Toggle button clicked!")  # Debug
        self.use_icons = not self.use_icons

        # Update button text
        if self.use_icons:
            self.toggle_button.setTitle_("Use Text")
        else:
            self.toggle_button.setTitle_("Use Icons")

        # Update the keyboard monitor to use the new display mode
        if self.keyboard_monitor:
            self.keyboard_monitor.use_icons = self.use_icons
            # Clear current display to force refresh
            self.update_keys_display([])

    @objc.IBAction
    def quitApp_(self, sender):
        """Quit the application cleanly"""
        print("Quit button clicked!")  # Debug
        print("Quitting KeyCast...")

        # Stop keyboard monitoring
        if self.keyboard_monitor:
            self.keyboard_monitor.stop()

        # Terminate the application
        NSApplication.sharedApplication().terminate_(self)

    def update_keys_display(self, keys):
        """Update the display with current keys"""
        if not keys:
            self.keys_label.setStringValue_("Press any keys...")
            self.keys_label.setTextColor_(NSColor.secondaryLabelColor())
            self.description_label.setStringValue_("")
        else:
            # Join keys with + for multi-key combinations
            display_text = " + ".join(keys)
            self.keys_label.setStringValue_(display_text)
            self.keys_label.setTextColor_(NSColor.labelColor())

            # Look up shortcut description
            description = self.shortcut_lookup.lookup(display_text)
            if description:
                self.description_label.setStringValue_(description)
                self.description_label.setTextColor_(NSColor.systemBlueColor())
            else:
                self.description_label.setStringValue_("")

    def run(self):
        """Run the application"""
        # Setup UI
        app = self.setup_ui()

        # Start keyboard monitoring
        self.keyboard_monitor = KeyboardMonitor(self.update_keys_display)
        self.keyboard_monitor.use_icons = self.use_icons
        self.keyboard_monitor.start()

        print("Hotkey Display is running. Window should be visible.")
        print("Press Cmd+Q to quit.")

        # Run the app
        app.run()

        # Cleanup
        if self.keyboard_monitor:
            self.keyboard_monitor.stop()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="KeyCast - Live Hotkey Display")
    parser.add_argument(
        "--text",
        action="store_true",
        help="Use text mode (CMD, CTRL) instead of icons (⌘, ⌃)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        help="Shortcut mode to load (basic, vscode, adobe, web, productivity, full)",
    )
    parser.add_argument(
        "--list-modes",
        action="store_true",
        help="List available modes and exit",
    )
    args = parser.parse_args()

    # Handle list modes
    if args.list_modes:
        lookup = ShortcutLookup()
        modes = lookup.get_available_modes()
        print("Available modes:")
        print("=" * 40)
        for mode_id, mode_info in modes.items():
            print(f"{mode_id:12} - {mode_info['name']}")
            print(f"{'':14} {mode_info['description']}")
            print()
        return 0

    print("KeyCast - Live Hotkey Display")
    print("=============================")
    print("This app shows the keys you're currently pressing.")
    print("It requires macOS Accessibility permissions.")

    display_mode = "text" if args.text else "icons"
    mode_info = f"mode: {args.mode}" if args.mode else "mode: all shortcuts"
    print(f"Display: {display_mode}, {mode_info}\n")

    try:
        app = HotkeyDisplayApp(use_icons=not args.text, mode=args.mode)
        app.run()
    except Exception as e:
        print(f"\n❌ Application failed to start: {e}")
        print("\nTroubleshooting:")
        print(
            "1. Open System Preferences > Security & Privacy > Privacy > Accessibility"
        )
        print("2. Look for 'Terminal' or 'Python' in the list")
        print(
            "3. If not present, click + and add it from /Applications/Utilities/Terminal.app"
        )
        print("4. Make sure the checkbox is checked")
        print("5. Try running the app again")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
