#!/usr/bin/env python3
"""
MemoKeys Native App - Keyboard Shortcut Practice Tool
Requires macOS Accessibility permissions for keyboard monitoring
"""

import sys
import json
import time
import threading
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Platform-specific imports
if sys.platform == "darwin":  # macOS
    from pynput import keyboard
    from AppKit import NSApplication, NSApp, NSWindow, NSView, NSTextField, NSButton
    from AppKit import NSMakeRect, NSFont, NSColor, NSTimer
    from AppKit import NSApplicationActivationPolicyRegular, NSTextAlignmentCenter
    import objc
else:
    print("This native app currently only supports macOS")
    sys.exit(1)


class ShortcutManager:
    """Manages shortcut data and checking logic"""

    def __init__(self):
        self.shortcuts_dir = Path(__file__).parent.parent / "data" / "shortcuts"
        self.current_shortcuts = []
        self.current_index = 0

    def load_shortcuts(self, category="system", filename="mac-basics.json"):
        """Load shortcuts from JSON file"""
        filepath = self.shortcuts_dir / category / filename
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                # Filter for mac shortcuts
                self.current_shortcuts = [
                    {
                        "action": s["action"],
                        "keys": s.get("mac", s.get("windows", "")),
                        "id": s["id"],
                    }
                    for s in data["shortcuts"]
                    if s.get("mac") or s.get("windows")
                ][
                    :5
                ]  # Limit to 5 for MVP
                self.current_index = 0
                return True
        except Exception as e:
            print(f"Error loading shortcuts: {e}")
            return False

    def get_current_shortcut(self):
        """Get the current shortcut to practice"""
        if 0 <= self.current_index < len(self.current_shortcuts):
            return self.current_shortcuts[self.current_index]
        return None

    def normalize_keys(self, keys):
        """Normalize key combination for comparison"""
        # Convert to lowercase and sort modifiers
        parts = keys.lower().replace(" ", "").split("+")
        modifiers = []
        main_key = ""

        for part in parts:
            if part in ["cmd", "command", "ctrl", "control", "alt", "option", "shift"]:
                # Normalize modifier names
                if part in ["cmd", "command"]:
                    modifiers.append("cmd")
                elif part in ["ctrl", "control"]:
                    modifiers.append("ctrl")
                elif part in ["alt", "option"]:
                    modifiers.append("alt")
                elif part == "shift":
                    modifiers.append("shift")
            else:
                main_key = part

        modifiers.sort()
        return "+".join(modifiers + [main_key])

    def check_shortcut(self, pressed_keys):
        """Check if pressed keys match current shortcut"""
        current = self.get_current_shortcut()
        if not current:
            return False

        expected = self.normalize_keys(current["keys"])
        actual = self.normalize_keys(pressed_keys)

        return expected == actual

    def next_shortcut(self):
        """Move to next shortcut"""
        self.current_index += 1
        return self.current_index < len(self.current_shortcuts)


class KeyboardMonitor:
    """Monitors keyboard input using pynput"""

    def __init__(self, callback):
        self.callback = callback
        self.current_keys = set()
        self.listener = None

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

    def _on_press(self, key):
        """Handle key press"""
        try:
            # Get key representation
            if hasattr(key, "char") and key.char:
                key_str = key.char.lower()
            elif hasattr(key, "name"):
                key_str = key.name.lower()
            else:
                key_str = str(key).lower()

            # Map special keys
            key_map = {
                "cmd": "cmd",
                "command": "cmd",
                "ctrl": "ctrl",
                "control": "ctrl",
                "alt": "alt",
                "option": "alt",
                "shift": "shift",
                "return": "enter",
                "space": "space",
            }

            if key_str in key_map:
                key_str = key_map[key_str]

            self.current_keys.add(key_str)

            # Check if we have a complete shortcut (modifier + key)
            modifiers = {"cmd", "ctrl", "alt", "shift"}
            has_modifier = any(m in self.current_keys for m in modifiers)
            non_modifiers = self.current_keys - modifiers

            if has_modifier and non_modifiers:
                # Build key combination string
                keys = []
                if "cmd" in self.current_keys:
                    keys.append("Cmd")
                if "ctrl" in self.current_keys:
                    keys.append("Ctrl")
                if "alt" in self.current_keys:
                    keys.append("Alt")
                if "shift" in self.current_keys:
                    keys.append("Shift")

                # Add non-modifier keys
                for k in sorted(non_modifiers):
                    keys.append(k.upper())

                combination = "+".join(keys)
                self.callback(combination)

        except Exception as e:
            print(f"Error in key press handler: {e}")

    def _on_release(self, key):
        """Handle key release"""
        try:
            if hasattr(key, "char") and key.char:
                key_str = key.char.lower()
            elif hasattr(key, "name"):
                key_str = key.name.lower()
            else:
                key_str = str(key).lower()

            # Clear keys on release
            self.current_keys.discard(key_str)

            # Also clear common variations
            key_variations = {
                "cmd": ["cmd", "command"],
                "ctrl": ["ctrl", "control"],
                "alt": ["alt", "option"],
            }

            for variant_list in key_variations.values():
                if key_str in variant_list:
                    for v in variant_list:
                        self.current_keys.discard(v)

        except Exception as e:
            print(f"Error in key release handler: {e}")


class MemoKeysApp:
    """Main application class"""

    def __init__(self):
        self.shortcut_manager = ShortcutManager()
        self.keyboard_monitor = None
        self.score = 0
        self.total_questions = 5
        self.results = []

        # UI elements (will be created in setup_ui)
        self.window = None
        self.prompt_label = None
        self.keys_label = None
        self.feedback_label = None
        self.score_label = None
        self.next_button = None

    def setup_ui(self):
        """Create the native macOS UI"""
        # Create application
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

        # Create window
        frame = NSMakeRect(100, 100, 600, 400)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            15,  # Titled | Closable | Miniaturizable | Resizable
            2,  # Buffered
            False,
        )
        self.window.setTitle_("MemoKeys - Keyboard Shortcut Practice")

        # Create content view
        content_view = NSView.alloc().initWithFrame_(frame)

        # Title label
        title_frame = NSMakeRect(20, 340, 560, 40)
        title_label = NSTextField.alloc().initWithFrame_(title_frame)
        title_label.setStringValue_("MemoKeys - Press the keyboard shortcut")
        title_label.setBezeled_(False)
        title_label.setDrawsBackground_(False)
        title_label.setEditable_(False)
        title_label.setFont_(NSFont.boldSystemFontOfSize_(24))
        title_label.setAlignment_(NSTextAlignmentCenter)
        content_view.addSubview_(title_label)

        # Prompt label (shows the action)
        prompt_frame = NSMakeRect(20, 250, 560, 60)
        self.prompt_label = NSTextField.alloc().initWithFrame_(prompt_frame)
        self.prompt_label.setStringValue_("Loading shortcuts...")
        self.prompt_label.setBezeled_(False)
        self.prompt_label.setDrawsBackground_(False)
        self.prompt_label.setEditable_(False)
        self.prompt_label.setFont_(NSFont.systemFontOfSize_(20))
        self.prompt_label.setAlignment_(NSTextAlignmentCenter)
        content_view.addSubview_(self.prompt_label)

        # Keys display label
        keys_frame = NSMakeRect(20, 180, 560, 50)
        self.keys_label = NSTextField.alloc().initWithFrame_(keys_frame)
        self.keys_label.setStringValue_("Press the shortcut...")
        self.keys_label.setBezeled_(True)
        self.keys_label.setDrawsBackground_(True)
        self.keys_label.setEditable_(False)
        self.keys_label.setFont_(NSFont.systemFontOfSize_(18))
        self.keys_label.setAlignment_(NSTextAlignmentCenter)
        content_view.addSubview_(self.keys_label)

        # Feedback label
        feedback_frame = NSMakeRect(20, 120, 560, 40)
        self.feedback_label = NSTextField.alloc().initWithFrame_(feedback_frame)
        self.feedback_label.setStringValue_("")
        self.feedback_label.setBezeled_(False)
        self.feedback_label.setDrawsBackground_(False)
        self.feedback_label.setEditable_(False)
        self.feedback_label.setFont_(NSFont.systemFontOfSize_(16))
        self.feedback_label.setAlignment_(NSTextAlignmentCenter)
        content_view.addSubview_(self.feedback_label)

        # Score label
        score_frame = NSMakeRect(20, 60, 560, 30)
        self.score_label = NSTextField.alloc().initWithFrame_(score_frame)
        self.score_label.setStringValue_(f"Score: {self.score}/{self.total_questions}")
        self.score_label.setBezeled_(False)
        self.score_label.setDrawsBackground_(False)
        self.score_label.setEditable_(False)
        self.score_label.setFont_(NSFont.systemFontOfSize_(14))
        self.score_label.setAlignment_(NSTextAlignmentCenter)
        content_view.addSubview_(self.score_label)

        # Next/Skip button
        button_frame = NSMakeRect(250, 20, 100, 30)
        self.next_button = NSButton.alloc().initWithFrame_(button_frame)
        self.next_button.setTitle_("Skip")
        self.next_button.setTarget_(self)
        self.next_button.setAction_("skipQuestion:")
        content_view.addSubview_(self.next_button)

        # Set content view
        self.window.setContentView_(content_view)

        # Show window
        self.window.makeKeyAndOrderFront_(None)

        return app

    def run(self):
        """Run the application"""
        # Load shortcuts
        if not self.shortcut_manager.load_shortcuts():
            print("Failed to load shortcuts")
            return

        # Setup UI
        app = self.setup_ui()

        # Start keyboard monitoring
        self.keyboard_monitor = KeyboardMonitor(self.handle_key_combination)
        self.keyboard_monitor.start()

        # Show first question
        self.show_current_question()

        # Run the app
        app.run()

    def show_current_question(self):
        """Display the current shortcut to practice"""
        shortcut = self.shortcut_manager.get_current_shortcut()
        if shortcut:
            self.prompt_label.setStringValue_(shortcut["action"])
            self.keys_label.setStringValue_("Press the shortcut...")
            self.feedback_label.setStringValue_("")
            self.update_score_display()
        else:
            self.show_results()

    def handle_key_combination(self, keys):
        """Handle keyboard shortcut input"""
        # Update display
        self.keys_label.setStringValue_(keys)

        # Check if correct
        if self.shortcut_manager.check_shortcut(keys):
            self.feedback_label.setStringValue_("✅ Correct!")
            self.feedback_label.setTextColor_(NSColor.greenColor())
            self.score += 1
            self.record_result(True, keys)

            # Move to next after delay
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                2.0, self, "nextQuestion:", None, False
            )
        else:
            current = self.shortcut_manager.get_current_shortcut()
            self.feedback_label.setStringValue_(f"❌ Correct: {current['keys']}")
            self.feedback_label.setTextColor_(NSColor.redColor())
            self.record_result(False, keys)

            # Move to next after delay
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                2.0, self, "nextQuestion:", None, False
            )

    def record_result(self, correct, user_keys):
        """Record the result for this question"""
        current = self.shortcut_manager.get_current_shortcut()
        self.results.append(
            {
                "action": current["action"],
                "correct_keys": current["keys"],
                "user_keys": user_keys,
                "correct": correct,
            }
        )

    @objc.IBAction
    def skipQuestion_(self, sender):
        """Skip current question"""
        self.record_result(False, "Skipped")
        self.nextQuestion_(None)

    @objc.IBAction
    def nextQuestion_(self, timer):
        """Move to next question"""
        if self.shortcut_manager.next_shortcut():
            self.show_current_question()
        else:
            self.show_results()

    def update_score_display(self):
        """Update the score display"""
        current_q = self.shortcut_manager.current_index + 1
        self.score_label.setStringValue_(
            f"Question {current_q}/{self.total_questions} | Score: {self.score}"
        )

    def show_results(self):
        """Show final results"""
        # Stop keyboard monitoring
        if self.keyboard_monitor:
            self.keyboard_monitor.stop()

        # Calculate percentage
        percentage = int((self.score / self.total_questions) * 100)

        # Update UI for results
        self.prompt_label.setStringValue_(
            f"Test Complete! Score: {self.score}/{self.total_questions} ({percentage}%)"
        )
        self.keys_label.setStringValue_("Thank you for practicing!")

        # Show performance message
        if percentage >= 90:
            msg = "🏆 Outstanding! You're a keyboard shortcut master!"
        elif percentage >= 70:
            msg = "🎯 Great job! You know your shortcuts well."
        elif percentage >= 50:
            msg = "👍 Good effort! Keep practicing to improve."
        else:
            msg = "💪 Keep learning! Shortcuts will save you time."

        self.feedback_label.setStringValue_(msg)
        self.feedback_label.setTextColor_(NSColor.blackColor())

        # Change button to "Quit"
        self.next_button.setTitle_("Quit")
        self.next_button.setAction_("terminate:")

        # Print detailed results
        print("\n=== Detailed Results ===")
        for i, result in enumerate(self.results, 1):
            status = "✅" if result["correct"] else "❌"
            print(f"{i}. {result['action']}: {status}")
            print(f"   Correct: {result['correct_keys']}")
            if not result["correct"]:
                print(f"   Your answer: {result['user_keys']}")
            print()


def main():
    """Main entry point"""
    print("MemoKeys Native App")
    print("===================")
    print("This app requires macOS Accessibility permissions.")
    print("Please grant permission when prompted.\n")

    try:
        app = MemoKeysApp()
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
