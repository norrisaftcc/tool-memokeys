#!/usr/bin/env python3
"""
Test suite for hotkey filtering improvements in Issue #2
Tests the core filtering logic that was implemented in Swift overlay

This test suite validates:
1. Filtering logic for meaningful shortcuts only
2. Helper function behavior for key display and action mapping
3. Edge cases and boundary conditions
4. Regression testing for existing functionality
"""

import unittest
from typing import List, Set
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockModifierFlags:
    """Mock class to simulate NSEvent.ModifierFlags behavior"""
    def __init__(self, command=False, shift=False, option=False, control=False):
        self.flags = set()
        if command:
            self.flags.add('command')
        if shift:
            self.flags.add('shift')
        if option:
            self.flags.add('option')
        if control:
            self.flags.add('control')
    
    def contains(self, flag: str) -> bool:
        return flag in self.flags


class HotkeyFilteringLogic:
    """Python implementation of the Swift filtering logic for testing"""
    
    @staticmethod
    def has_valid_modifiers(modifiers: MockModifierFlags, key: str) -> bool:
        """
        Port of hasValidModifiers from Swift implementation
        Must have at least one primary modifier (⌘, ⌥, ⌃) OR meaningful shift combination
        """
        has_primary_modifier = (modifiers.contains('command') or 
                               modifiers.contains('option') or 
                               modifiers.contains('control'))
        
        # Allow shift only with specific keys or in combination with other modifiers
        has_meaningful_shift = (modifiers.contains('shift') and 
                               (has_primary_modifier or HotkeyFilteringLogic.is_special_shift_key(key)))
        
        return has_primary_modifier or has_meaningful_shift
    
    @staticmethod
    def has_any_meaningful_modifier(modifiers: MockModifierFlags) -> bool:
        """Port of hasAnyMeaningfulModifier from Swift implementation"""
        return (modifiers.contains('command') or 
                modifiers.contains('option') or 
                modifiers.contains('control'))
    
    @staticmethod
    def is_special_shift_key(key: str) -> bool:
        """Port of isSpecialShiftKey from Swift implementation"""
        special_keys = ["TAB", "SPACE", "RETURN", "DELETE", "ESCAPE"]
        return key in special_keys
    
    @staticmethod
    def get_key_display_name(key: str) -> str:
        """Port of getKeyDisplayName from Swift implementation"""
        key_mapping = {
            " ": "SPACE",
            "\t": "TAB",
            "\r": "RETURN",
            "\n": "RETURN",
            chr(27): "ESC",
            chr(127): "DELETE"
        }
        return key_mapping.get(key, key)
    
    @staticmethod
    def get_action_description(modifiers: List[str], key: str) -> str:
        """Port of getActionDescription from Swift implementation"""
        combo = "".join(modifiers) + key
        
        action_map = {
            "⌘C": "Copy",
            "⌘V": "Paste", 
            "⌘X": "Cut",
            "⌘Z": "Undo",
            "⌘⇧Z": "Redo",
            "⌘S": "Save",
            "⌘⇧S": "Save As",
            "⌘O": "Open",
            "⌘N": "New",
            "⌘W": "Close",
            "⌘Q": "Quit",
            "⌘A": "Select All",
            "⌘F": "Find",
            "⌘G": "Find Next",
            "⌘⇧G": "Find Previous",
            "⌘P": "Print",
            "⌘,": "Preferences",
            "⌘TAB": "Switch App",
            "⌘`": "Switch Window",
            "⌘SPACE": "Spotlight",
            "⌘⌥D": "Show/Hide Dock",
            "⌘⌥ESC": "Force Quit",
            "⌘⇧3": "Screenshot",
            "⌘⇧4": "Screenshot Selection", 
            "⌘⇧5": "Screenshot/Recording"
        }
        
        return action_map.get(combo, "")


class TestHotkeyFiltering(unittest.TestCase):
    """Test cases for hotkey filtering logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.filter_logic = HotkeyFilteringLogic()
    
    def test_single_letter_filtering(self):
        """Test that single letters without modifiers are filtered out"""
        # Test regular letters - should be filtered out
        single_letter_modifiers = MockModifierFlags()
        
        self.assertFalse(
            self.filter_logic.has_valid_modifiers(single_letter_modifiers, "A"),
            "Single letter 'A' should be filtered out"
        )
        
        self.assertFalse(
            self.filter_logic.has_valid_modifiers(single_letter_modifiers, "Z"),
            "Single letter 'Z' should be filtered out"
        )
        
        self.assertFalse(
            self.filter_logic.has_valid_modifiers(single_letter_modifiers, "1"),
            "Single number '1' should be filtered out"
        )
    
    def test_command_key_combinations(self):
        """Test that Command key combinations are allowed"""
        command_modifiers = MockModifierFlags(command=True)
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(command_modifiers, "C"),
            "⌘+C should be allowed"
        )
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(command_modifiers, "V"),
            "⌘+V should be allowed"
        )
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(command_modifiers, "SPACE"),
            "⌘+SPACE should be allowed"
        )
    
    def test_option_key_combinations(self):
        """Test that Option key combinations are allowed"""
        option_modifiers = MockModifierFlags(option=True)
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(option_modifiers, "D"),
            "⌥+D should be allowed"
        )
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(option_modifiers, "TAB"),
            "⌥+TAB should be allowed"
        )
    
    def test_control_key_combinations(self):
        """Test that Control key combinations are allowed"""
        control_modifiers = MockModifierFlags(control=True)
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(control_modifiers, "A"),
            "⌃+A should be allowed"
        )
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(control_modifiers, "C"),
            "⌃+C should be allowed"
        )
    
    def test_shift_only_combinations(self):
        """Test that Shift-only combinations are properly filtered"""
        shift_modifiers = MockModifierFlags(shift=True)
        
        # Regular letters with shift should be filtered out
        self.assertFalse(
            self.filter_logic.has_valid_modifiers(shift_modifiers, "A"),
            "⇧+A should be filtered out (just capitalization)"
        )
        
        # Special keys with shift should be allowed
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(shift_modifiers, "TAB"),
            "⇧+TAB should be allowed"
        )
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(shift_modifiers, "SPACE"),
            "⇧+SPACE should be allowed"
        )
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(shift_modifiers, "RETURN"),
            "⇧+RETURN should be allowed"
        )
    
    def test_multiple_modifier_combinations(self):
        """Test combinations with multiple modifiers"""
        cmd_shift_modifiers = MockModifierFlags(command=True, shift=True)
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(cmd_shift_modifiers, "Z"),
            "⌘+⇧+Z should be allowed"
        )
        
        cmd_option_modifiers = MockModifierFlags(command=True, option=True)
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(cmd_option_modifiers, "ESC"),
            "⌘+⌥+ESC should be allowed"
        )
    
    def test_special_shift_keys(self):
        """Test the special shift key identification"""
        special_keys = ["TAB", "SPACE", "RETURN", "DELETE", "ESCAPE"]
        
        for key in special_keys:
            self.assertTrue(
                self.filter_logic.is_special_shift_key(key),
                f"{key} should be recognized as special shift key"
            )
        
        # Regular letters should not be special
        self.assertFalse(
            self.filter_logic.is_special_shift_key("A"),
            "Regular letter 'A' should not be special shift key"
        )
    
    def test_key_display_names(self):
        """Test key display name mapping"""
        test_cases = [
            (" ", "SPACE"),
            ("\t", "TAB"),
            ("\r", "RETURN"),
            ("\n", "RETURN"),
            (chr(27), "ESC"),
            (chr(127), "DELETE"),
            ("A", "A"),  # Regular keys unchanged
            ("1", "1")   # Numbers unchanged
        ]
        
        for input_key, expected_output in test_cases:
            self.assertEqual(
                self.filter_logic.get_key_display_name(input_key),
                expected_output,
                f"Key '{repr(input_key)}' should display as '{expected_output}'"
            )
    
    def test_action_descriptions(self):
        """Test action description mapping for common shortcuts"""
        test_cases = [
            (["⌘"], "C", "Copy"),
            (["⌘"], "V", "Paste"),
            (["⌘"], "X", "Cut"),
            (["⌘"], "Z", "Undo"),
            (["⌘", "⇧"], "Z", "Redo"),
            (["⌘"], "S", "Save"),
            (["⌘", "⇧"], "S", "Save As"),
            (["⌘"], "SPACE", "Spotlight"),
            (["⌘", "⌥"], "ESC", "Force Quit"),
            (["⌘"], "Q", "Quit"),
            (["⌘"], "UNKNOWN", "")  # Unknown combination should return empty
        ]
        
        for modifiers, key, expected_description in test_cases:
            self.assertEqual(
                self.filter_logic.get_action_description(modifiers, key),
                expected_description,
                f"Combination {'+'.join(modifiers)}+{key} should describe as '{expected_description}'"
            )
    
    def test_meaningful_modifier_detection(self):
        """Test meaningful modifier detection"""
        # Primary modifiers should be meaningful
        self.assertTrue(
            self.filter_logic.has_any_meaningful_modifier(MockModifierFlags(command=True)),
            "Command should be meaningful"
        )
        
        self.assertTrue(
            self.filter_logic.has_any_meaningful_modifier(MockModifierFlags(option=True)),
            "Option should be meaningful"
        )
        
        self.assertTrue(
            self.filter_logic.has_any_meaningful_modifier(MockModifierFlags(control=True)),
            "Control should be meaningful"
        )
        
        # Shift alone should not be meaningful
        self.assertFalse(
            self.filter_logic.has_any_meaningful_modifier(MockModifierFlags(shift=True)),
            "Shift alone should not be meaningful"
        )
        
        # No modifiers should not be meaningful
        self.assertFalse(
            self.filter_logic.has_any_meaningful_modifier(MockModifierFlags()),
            "No modifiers should not be meaningful"
        )


class TestFilteringEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.filter_logic = HotkeyFilteringLogic()
    
    def test_empty_key_input(self):
        """Test behavior with empty key input"""
        command_modifiers = MockModifierFlags(command=True)
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(command_modifiers, ""),
            "Empty key with command modifier should be valid"
        )
    
    def test_unicode_characters(self):
        """Test behavior with unicode characters"""
        command_modifiers = MockModifierFlags(command=True)
        
        unicode_chars = ["€", "©", "™", "∑", "π"]
        for char in unicode_chars:
            self.assertTrue(
                self.filter_logic.has_valid_modifiers(command_modifiers, char),
                f"Unicode character '{char}' with command should be valid"
            )
    
    def test_case_sensitivity(self):
        """Test case sensitivity in key handling"""
        command_modifiers = MockModifierFlags(command=True)
        
        # Both uppercase and lowercase should work
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(command_modifiers, "c"),
            "Lowercase 'c' with command should be valid"
        )
        
        self.assertTrue(
            self.filter_logic.has_valid_modifiers(command_modifiers, "C"),
            "Uppercase 'C' with command should be valid"
        )
    
    def test_special_characters(self):
        """Test special characters and symbols"""
        command_modifiers = MockModifierFlags(command=True)
        
        special_chars = [",", ".", "/", ";", "'", "[", "]", "\\", "`", "=", "-"]
        for char in special_chars:
            self.assertTrue(
                self.filter_logic.has_valid_modifiers(command_modifiers, char),
                f"Special character '{char}' with command should be valid"
            )


class TestRegressionScenarios(unittest.TestCase):
    """Test regression scenarios to ensure existing functionality works"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.filter_logic = HotkeyFilteringLogic()
    
    def test_common_macos_shortcuts_recognized(self):
        """Test that common macOS shortcuts are properly recognized"""
        common_shortcuts = [
            (MockModifierFlags(command=True), "C", True, "Copy"),
            (MockModifierFlags(command=True), "V", True, "Paste"),
            (MockModifierFlags(command=True), "X", True, "Cut"),
            (MockModifierFlags(command=True), "Z", True, "Undo"),
            (MockModifierFlags(command=True, shift=True), "Z", True, "Redo"),
            (MockModifierFlags(command=True), "S", True, "Save"),
            (MockModifierFlags(command=True), "A", True, "Select All"),
            (MockModifierFlags(command=True), "F", True, "Find"),
            (MockModifierFlags(command=True), "Q", True, "Quit")
        ]
        
        for modifiers, key, should_be_valid, expected_action in common_shortcuts:
            # Test filtering
            self.assertEqual(
                self.filter_logic.has_valid_modifiers(modifiers, key),
                should_be_valid,
                f"Shortcut with key '{key}' validity mismatch"
            )
            
            # Test action description
            modifier_symbols = []
            if modifiers.contains('command'):
                modifier_symbols.append('⌘')
            if modifiers.contains('shift'):
                modifier_symbols.append('⇧')
            if modifiers.contains('option'):
                modifier_symbols.append('⌥')
            if modifiers.contains('control'):
                modifier_symbols.append('⌃')
            
            actual_action = self.filter_logic.get_action_description(modifier_symbols, key)
            self.assertEqual(
                actual_action,
                expected_action,
                f"Action description for {'+'.join(modifier_symbols)}+{key} should be '{expected_action}'"
            )
    
    def test_application_switching_shortcuts(self):
        """Test application and window switching shortcuts"""
        app_shortcuts = [
            (MockModifierFlags(command=True), "TAB", True, "Switch App"),
            (MockModifierFlags(command=True), "`", True, "Switch Window")
        ]
        
        for modifiers, key, should_be_valid, expected_action in app_shortcuts:
            self.assertEqual(
                self.filter_logic.has_valid_modifiers(modifiers, key),
                should_be_valid,
                f"App switching shortcut {key} should be valid"
            )
    
    def test_system_shortcuts(self):
        """Test system-level shortcuts"""
        system_shortcuts = [
            (MockModifierFlags(command=True), "SPACE", True, "Spotlight"),
            (MockModifierFlags(command=True, option=True), "ESC", True, "Force Quit"),
            (MockModifierFlags(command=True, shift=True), "3", True, "Screenshot"),
            (MockModifierFlags(command=True, shift=True), "4", True, "Screenshot Selection")
        ]
        
        for modifiers, key, should_be_valid, expected_action in system_shortcuts:
            self.assertEqual(
                self.filter_logic.has_valid_modifiers(modifiers, key),
                should_be_valid,
                f"System shortcut {key} should be valid"
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)