#!/usr/bin/env python3
"""
MemoKeys MVP - macOS Floating Overlay for Keyboard Shortcut Practice
Requires macOS Accessibility permissions
"""

import sys
import json
import threading
from pathlib import Path
from datetime import datetime

if sys.platform != "darwin":
    print("This app requires macOS")
    sys.exit(1)

from pynput import keyboard
from AppKit import (
    NSApplication, NSApp, NSWindow, NSView, NSTextField, NSButton,
    NSMakeRect, NSFont, NSColor, NSTimer, NSWindowStyleMaskTitled,
    NSWindowStyleMaskClosable, NSWindowStyleMaskResizable,
    NSBackingStoreBuffered, NSApplicationActivationPolicyAccessory,
    NSWindowCollectionBehaviorCanJoinAllSpaces, NSWindowLevel,
    NSTextAlignmentCenter, NSWindowStyleMaskFullSizeContentView
)
import objc


class MemoKeysOverlay:
    """Main application class for MemoKeys floating overlay"""
    
    def __init__(self):
        self.shortcuts = [
            {"keys": "⌘+C", "action": "Copy", "id": "copy"},
            {"keys": "⌘+V", "action": "Paste", "id": "paste"},
            {"keys": "⌘+X", "action": "Cut", "id": "cut"},
            {"keys": "⌘+Z", "action": "Undo", "id": "undo"},
            {"keys": "⌘+S", "action": "Save", "id": "save"}
        ]
        self.current_index = 0
        self.score = 0
        self.total_attempts = 0
        self.pressed_keys = set()
        self.listening = False
        
        # UI elements
        self.window = None
        self.prompt_label = None
        self.keys_label = None
        self.feedback_label = None
        self.score_label = None
        self.start_button = None
        
        # Keyboard listener
        self.keyboard_listener = None
        
    def create_window(self):
        """Create the floating overlay window"""
        # Window configuration
        frame = NSMakeRect(100, 100, 400, 200)
        style_mask = (NSWindowStyleMaskTitled | 
                     NSWindowStyleMaskClosable | 
                     NSWindowStyleMaskResizable)
        
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame, style_mask, NSBackingStoreBuffered, False
        )
        
        # Make it float above all windows
        self.window.setLevel_(NSWindowLevel.floating)
        self.window.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
        self.window.setTitle_("MemoKeys")
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.colorWithWhite_alpha_(0.1, 0.95))
        
        # Create content view
        content_view = NSView.alloc().initWithFrame_(frame)
        
        # Prompt label (what to press)
        self.prompt_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 140, 360, 30))
        self.prompt_label.setStringValue_("Welcome to MemoKeys!")
        self.prompt_label.setBezeled_(False)
        self.prompt_label.setDrawsBackground_(False)
        self.prompt_label.setEditable_(False)
        self.prompt_label.setSelectable_(False)
        self.prompt_label.setAlignment_(NSTextAlignmentCenter)
        self.prompt_label.setFont_(NSFont.systemFontOfSize_(16))
        self.prompt_label.setTextColor_(NSColor.whiteColor())
        
        # Keys display (visual feedback)
        self.keys_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 90, 360, 40))
        self.keys_label.setStringValue_("")
        self.keys_label.setBezeled_(False)
        self.keys_label.setDrawsBackground_(False)
        self.keys_label.setEditable_(False)
        self.keys_label.setSelectable_(False)
        self.keys_label.setAlignment_(NSTextAlignmentCenter)
        self.keys_label.setFont_(NSFont.boldSystemFontOfSize_(24))
        self.keys_label.setTextColor_(NSColor.cyanColor())
        
        # Feedback label (correct/incorrect)
        self.feedback_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 60, 360, 25))
        self.feedback_label.setStringValue_("")
        self.feedback_label.setBezeled_(False)
        self.feedback_label.setDrawsBackground_(False)
        self.feedback_label.setEditable_(False)
        self.feedback_label.setSelectable_(False)
        self.feedback_label.setAlignment_(NSTextAlignmentCenter)
        self.feedback_label.setFont_(NSFont.systemFontOfSize_(14))
        
        # Score label
        self.score_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 35, 180, 20))
        self.score_label.setStringValue_("Score: 0/0")
        self.score_label.setBezeled_(False)
        self.score_label.setDrawsBackground_(False)
        self.score_label.setEditable_(False)
        self.score_label.setSelectable_(False)
        self.score_label.setFont_(NSFont.systemFontOfSize_(12))
        self.score_label.setTextColor_(NSColor.whiteColor())
        
        # Start/Reset button
        self.start_button = NSButton.alloc().initWithFrame_(NSMakeRect(280, 30, 100, 30))
        self.start_button.setTitle_("Start Practice")
        self.start_button.setTarget_(self)
        self.start_button.setAction_(objc.selector(self.start_practice, signature=b'v@:'))
        self.start_button.setBezelStyle_(1)
        
        # Add all subviews
        content_view.addSubview_(self.prompt_label)
        content_view.addSubview_(self.keys_label)
        content_view.addSubview_(self.feedback_label)
        content_view.addSubview_(self.score_label)
        content_view.addSubview_(self.start_button)
        
        self.window.setContentView_(content_view)
        self.window.makeKeyAndOrderFront_(None)
        
    def start_practice(self):
        """Start or reset practice session"""
        self.current_index = 0
        self.score = 0
        self.total_attempts = 0
        self.listening = True
        
        self.start_button.setTitle_("Reset")
        self.feedback_label.setStringValue_("")
        self.show_next_shortcut()
        
        # Start keyboard listener if not running
        if not self.keyboard_listener:
            self.start_keyboard_listener()
    
    def show_next_shortcut(self):
        """Display the next shortcut to practice"""
        if self.current_index < len(self.shortcuts):
            shortcut = self.shortcuts[self.current_index]
            self.prompt_label.setStringValue_(f"Press: {shortcut['action']}")
            self.keys_label.setStringValue_(shortcut['keys'])
            self.keys_label.setTextColor_(NSColor.grayColor())
        else:
            # Practice complete
            self.listening = False
            self.prompt_label.setStringValue_("Practice Complete!")
            percentage = int((self.score / self.total_attempts) * 100) if self.total_attempts > 0 else 0
            self.keys_label.setStringValue_(f"Final Score: {self.score}/{self.total_attempts} ({percentage}%)")
            self.keys_label.setTextColor_(NSColor.greenColor())
    
    def check_shortcut(self):
        """Check if the pressed keys match the current shortcut"""
        if not self.listening or self.current_index >= len(self.shortcuts):
            return
        
        current = self.shortcuts[self.current_index]
        pressed = self.get_pressed_combination()
        
        self.total_attempts += 1
        
        if self.normalize_keys(pressed) == self.normalize_keys(current['keys']):
            # Correct!
            self.score += 1
            self.feedback_label.setStringValue_("✓ Correct!")
            self.feedback_label.setTextColor_(NSColor.greenColor())
            self.keys_label.setTextColor_(NSColor.greenColor())
            
            # Move to next after delay
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                1.0, self, objc.selector(self.next_shortcut, signature=b'v@:'), None, False
            )
        else:
            # Incorrect
            self.feedback_label.setStringValue_(f"✗ Try again! (You pressed: {pressed})")
            self.feedback_label.setTextColor_(NSColor.redColor())
            self.keys_label.setTextColor_(NSColor.orangeColor())
        
        self.update_score()
    
    def next_shortcut(self):
        """Move to the next shortcut"""
        self.current_index += 1
        self.feedback_label.setStringValue_("")
        self.show_next_shortcut()
    
    def update_score(self):
        """Update the score display"""
        self.score_label.setStringValue_(f"Score: {self.score}/{self.total_attempts}")
    
    def normalize_keys(self, keys):
        """Normalize key combination for comparison"""
        return keys.lower().replace(" ", "").replace("cmd", "⌘").replace("command", "⌘")
    
    def get_pressed_combination(self):
        """Get the current pressed key combination"""
        combo = []
        if 'cmd' in self.pressed_keys or '⌘' in self.pressed_keys:
            combo.append('⌘')
        if 'shift' in self.pressed_keys or '⇧' in self.pressed_keys:
            combo.append('⇧')
        if 'option' in self.pressed_keys or 'alt' in self.pressed_keys or '⌥' in self.pressed_keys:
            combo.append('⌥')
        if 'ctrl' in self.pressed_keys or 'control' in self.pressed_keys or '⌃' in self.pressed_keys:
            combo.append('⌃')
        
        # Add the main key
        for key in self.pressed_keys:
            if key not in ['cmd', '⌘', 'shift', '⇧', 'option', 'alt', '⌥', 'ctrl', 'control', '⌃']:
                combo.append(key.upper())
                break
        
        return '+'.join(combo)
    
    def start_keyboard_listener(self):
        """Start the keyboard event listener"""
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    self.pressed_keys.add(key.char.lower())
                elif hasattr(key, 'name'):
                    if key == keyboard.Key.cmd:
                        self.pressed_keys.add('cmd')
                    elif key == keyboard.Key.shift:
                        self.pressed_keys.add('shift')
                    elif key == keyboard.Key.alt:
                        self.pressed_keys.add('option')
                    elif key == keyboard.Key.ctrl:
                        self.pressed_keys.add('ctrl')
                
                # Check if this completes a shortcut
                if self.listening and len(self.pressed_keys) >= 2:
                    self.check_shortcut()
            except Exception as e:
                print(f"Error in key press: {e}")
        
        def on_release(key):
            try:
                # Clear keys on release
                if hasattr(key, 'char') and key.char:
                    self.pressed_keys.discard(key.char.lower())
                elif hasattr(key, 'name'):
                    if key == keyboard.Key.cmd:
                        self.pressed_keys.discard('cmd')
                    elif key == keyboard.Key.shift:
                        self.pressed_keys.discard('shift')
                    elif key == keyboard.Key.alt:
                        self.pressed_keys.discard('option')
                    elif key == keyboard.Key.ctrl:
                        self.pressed_keys.discard('ctrl')
                
                # Clear all if no modifiers held
                if not any(k in self.pressed_keys for k in ['cmd', 'shift', 'option', 'ctrl']):
                    self.pressed_keys.clear()
                    
            except Exception as e:
                print(f"Error in key release: {e}")
        
        self.keyboard_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.keyboard_listener.start()
    
    def run(self):
        """Run the application"""
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        self.create_window()
        
        # Run the app
        app.run()


if __name__ == "__main__":
    print("Starting MemoKeys...")
    print("Note: This app requires macOS Accessibility permissions.")
    print("Please grant access in System Preferences > Security & Privacy > Accessibility")
    
    app = MemoKeysOverlay()
    app.run()