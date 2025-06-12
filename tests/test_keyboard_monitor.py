#!/usr/bin/env python3
"""
Tests for KeyboardMonitor functionality (without actual keyboard input)
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to sys.path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the pynput dependency for testing
sys.modules['pynput'] = Mock()
sys.modules['pynput.keyboard'] = Mock()

from hotkey_panel_proto.hotkey_display import KeyboardMonitor


class MockKey:
    """Mock key object for testing"""
    def __init__(self, char=None, name=None):
        if char:
            self.char = char
        if name:
            self.name = name


class TestKeyboardMonitor:
    """Test KeyboardMonitor functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.callback_results = []
        
        def test_callback(keys):
            self.callback_results.append(keys.copy() if keys else [])
            
        self.monitor = KeyboardMonitor(test_callback)
        
    def test_get_key_name_icons(self):
        """Test key name generation in icon mode"""
        self.monitor.use_icons = True
        
        # Test character keys
        char_key = MockKey(char='a')
        assert self.monitor._get_key_name(char_key) == 'A'
        
        # Test modifier keys with icons
        cmd_key = MockKey(name='cmd')
        assert self.monitor._get_key_name(cmd_key) == '⌘'
        
        ctrl_key = MockKey(name='ctrl')
        assert self.monitor._get_key_name(ctrl_key) == '⌃'
        
        alt_key = MockKey(name='alt')
        assert self.monitor._get_key_name(alt_key) == '⌥'
        
        shift_key = MockKey(name='shift')
        assert self.monitor._get_key_name(shift_key) == '⇧'
        
        # Test special keys
        space_key = MockKey(name='space')
        assert self.monitor._get_key_name(space_key) == '␣'
        
        enter_key = MockKey(name='return')
        assert self.monitor._get_key_name(enter_key) == '↩'
        
    def test_get_key_name_text(self):
        """Test key name generation in text mode"""
        self.monitor.use_icons = False
        
        # Test modifier keys with text
        cmd_key = MockKey(name='cmd')
        assert self.monitor._get_key_name(cmd_key) == 'CMD'
        
        ctrl_key = MockKey(name='ctrl')
        assert self.monitor._get_key_name(ctrl_key) == 'CTRL'
        
        alt_key = MockKey(name='option')
        assert self.monitor._get_key_name(alt_key) == 'ALT'
        
        shift_key = MockKey(name='shift')
        assert self.monitor._get_key_name(shift_key) == 'SHIFT'
        
        # Test special keys
        space_key = MockKey(name='space')
        assert self.monitor._get_key_name(space_key) == 'SPACE'
        
        enter_key = MockKey(name='return')
        assert self.monitor._get_key_name(enter_key) == 'ENTER'
        
    def test_should_display_key(self):
        """Test key filtering logic"""
        # Single letters should not display without modifiers
        assert not self.monitor._should_display_key('A')
        assert not self.monitor._should_display_key('z')
        
        # Add a modifier key
        self.monitor.current_keys['⌘'] = True
        
        # Now single letters should display
        assert self.monitor._should_display_key('A')
        assert self.monitor._should_display_key('z')
        
        # Special keys should always display
        assert self.monitor._should_display_key('⌘')
        assert self.monitor._should_display_key('ENTER')
        assert self.monitor._should_display_key('F1')
        
    def test_key_press_simulation(self):
        """Test simulated key press handling"""
        # Simulate pressing Cmd
        cmd_key = MockKey(name='cmd')
        self.monitor._on_press(cmd_key)
        
        # Should have the cmd key in current_keys
        assert '⌘' in self.monitor.current_keys
        
        # But callback should not fire yet (no displayable keys)
        assert len(self.callback_results) == 1
        assert self.callback_results[0] == []
        
        # Now press 'C'
        c_key = MockKey(char='c')
        self.monitor._on_press(c_key)
        
        # Should have both keys
        assert '⌘' in self.monitor.current_keys
        assert 'C' in self.monitor.current_keys
        
        # Callback should fire with both keys
        assert len(self.callback_results) == 2
        assert '⌘' in self.callback_results[1]
        assert 'C' in self.callback_results[1]
        
    def test_key_release_simulation(self):
        """Test simulated key release handling"""
        # Set up initial state
        self.monitor.current_keys['⌘'] = True
        self.monitor.current_keys['C'] = True
        
        # Release 'C'
        c_key = MockKey(char='c')
        self.monitor._on_release(c_key)
        
        # Should only have Cmd left
        assert '⌘' in self.monitor.current_keys
        assert 'C' not in self.monitor.current_keys
        
        # Callback should fire with empty list (no displayable keys)
        assert len(self.callback_results) == 1
        assert self.callback_results[0] == []
        
        # Release Cmd
        cmd_key = MockKey(name='cmd')
        self.monitor._on_release(cmd_key)
        
        # Should have no keys left
        assert len(self.monitor.current_keys) == 0
        
        # Callback should fire with empty list
        assert len(self.callback_results) == 2
        assert self.callback_results[1] == []
        
    def test_mode_switching(self):
        """Test switching between icon and text modes"""
        # Start in icon mode
        self.monitor.use_icons = True
        cmd_key = MockKey(name='cmd')
        assert self.monitor._get_key_name(cmd_key) == '⌘'
        
        # Switch to text mode
        self.monitor.use_icons = False
        assert self.monitor._get_key_name(cmd_key) == 'CMD'
        
        # Switch back to icon mode
        self.monitor.use_icons = True
        assert self.monitor._get_key_name(cmd_key) == '⌘'


if __name__ == "__main__":
    pytest.main([__file__])