#!/usr/bin/env python3
"""
MemoKeys Minimal MVP - Just the floating overlay
"""

from AppKit import *
from pynput import keyboard
import objc

class MemoKeys:
    def __init__(self):
        self.window = None
        self.label = None
        self.keys_pressed = []
        
    def create_window(self):
        # Floating window
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((200, 200), (300, 100)),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            False
        )
        self.window.setLevel_(3)  # Floating window level
        self.window.setTitle_("MemoKeys")
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.blackColor().colorWithAlphaComponent_(0.8))
        
        # Text label
        self.label = NSTextField.alloc().initWithFrame_(((10, 20), (280, 60)))
        self.label.setStringValue_("Press ⌘+C")
        self.label.setBezeled_(False)
        self.label.setDrawsBackground_(False)
        self.label.setEditable_(False)
        self.label.setAlignment_(NSTextAlignmentCenter)
        self.label.setFont_(NSFont.systemFontOfSize_(24))
        self.label.setTextColor_(NSColor.whiteColor())
        
        self.window.contentView().addSubview_(self.label)
        self.window.makeKeyAndOrderFront_(None)
        
    def on_press(self, key):
        # Update display when keys pressed
        if hasattr(key, 'char'):
            self.keys_pressed.append(key.char)
        elif key == keyboard.Key.cmd:
            self.keys_pressed.append('⌘')
        
        display = '+'.join(self.keys_pressed[-2:])  # Show last 2 keys
        self.label.setStringValue_(display)
        
    def on_release(self, key):
        self.keys_pressed = []
        
    def run(self):
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        self.create_window()
        
        # Start keyboard listener
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        listener.start()
        
        app.run()

if __name__ == "__main__":
    MemoKeys().run()