#!/usr/bin/env python3
"""
Integration tests for KeyCast functionality
"""

import pytest
import tempfile
import json
from pathlib import Path
import sys
import os
from unittest.mock import patch, Mock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock GUI dependencies
sys.modules['pynput'] = Mock()
sys.modules['pynput.keyboard'] = Mock()
sys.modules['AppKit'] = Mock()

from hotkey_panel_proto.hotkey_display import ShortcutLookup, HotkeyDisplayApp


class TestIntegration:
    """Integration tests for complete KeyCast workflows"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Use the real shortcuts directory
        self.shortcuts_dir = Path("data/shortcuts")
        
    def test_real_mode_loading(self):
        """Test loading real modes with real data"""
        # Test that all defined modes work
        lookup = ShortcutLookup()
        modes = lookup.get_available_modes()
        
        assert len(modes) > 0, "No modes found in real data"
        
        for mode_id in modes.keys():
            mode_lookup = ShortcutLookup(mode=mode_id)
            assert len(mode_lookup.shortcuts) > 0, f"Mode {mode_id} loaded no shortcuts"
            
    def test_common_shortcuts_work(self):
        """Test that common shortcuts are found and work correctly"""
        lookup = ShortcutLookup()
        
        # Test common Mac shortcuts
        common_tests = [
            ("Cmd+C", "copy"),
            ("⌘+C", "copy"),
            ("Cmd+V", "paste"),
            ("⌘+V", "paste"),
            ("Cmd+Z", "undo"),
            ("Cmd+Space", "spotlight")
        ]
        
        for combo, expected_keyword in common_tests:
            result = lookup.lookup(combo)
            assert result is not None, f"No result found for {combo}"
            assert expected_keyword.lower() in result.lower(), f"Expected '{expected_keyword}' in result for {combo}, got: {result}"
            
    def test_vscode_mode_shortcuts(self):
        """Test VSCode mode specific shortcuts"""
        lookup = ShortcutLookup(mode="vscode")
        
        # Should have basic shortcuts
        assert lookup.lookup("Cmd+C") is not None
        
        # Should have VSCode specific shortcuts if they exist
        vscode_file = self.shortcuts_dir / "editors" / "vscode-shortcuts.json"
        if vscode_file.exists():
            with open(vscode_file, 'r') as f:
                data = json.load(f)
                
            # Test a few VSCode shortcuts
            for shortcut in data.get("shortcuts", [])[:3]:  # Test first 3
                if "mac" in shortcut:
                    result = lookup.lookup(shortcut["mac"])
                    assert result is not None, f"VSCode shortcut {shortcut['mac']} not found"
                    assert result == shortcut["action"]
                    
    def test_mode_vs_all_shortcuts(self):
        """Test that mode loading loads fewer shortcuts than all"""
        all_lookup = ShortcutLookup()
        basic_lookup = ShortcutLookup(mode="basic")
        
        assert len(basic_lookup.shortcuts) < len(all_lookup.shortcuts)
        assert len(basic_lookup.shortcuts) > 0
        
    def test_icon_vs_text_lookup(self):
        """Test that both icon and text formats work for lookup"""
        lookup = ShortcutLookup()
        
        # These should return the same result
        icon_result = lookup.lookup("⌘+C")
        text_result = lookup.lookup("Cmd+C")
        
        if icon_result is not None and text_result is not None:
            assert icon_result == text_result
            
    def test_app_initialization(self):
        """Test that HotkeyDisplayApp initializes correctly"""
        # Test default initialization
        app = HotkeyDisplayApp()
        assert app.use_icons == True
        assert app.mode is None
        assert app.shortcut_lookup is not None
        
        # Test with parameters
        app_text = HotkeyDisplayApp(use_icons=False, mode="basic")
        assert app_text.use_icons == False
        assert app_text.mode == "basic"
        assert app_text.shortcut_lookup.mode == "basic"
        
    def test_end_to_end_shortcut_lookup(self):
        """Test complete shortcut lookup workflow"""
        # Initialize app in VSCode mode
        app = HotkeyDisplayApp(mode="vscode")
        
        # Test that we can look up shortcuts through the app
        test_shortcuts = ["Cmd+C", "⌘+V", "Cmd+Z"]
        
        for shortcut in test_shortcuts:
            result = app.shortcut_lookup.lookup(shortcut)
            # Should find something for these basic shortcuts
            assert result is not None, f"No result for {shortcut} in vscode mode"
            
    def test_mode_file_consistency(self):
        """Test that modes.json is consistent with actual files"""
        lookup = ShortcutLookup()
        modes = lookup.get_available_modes()
        
        for mode_id, mode_info in modes.items():
            # All referenced files should exist
            for file_path in mode_info["files"]:
                full_path = self.shortcuts_dir / file_path
                assert full_path.exists(), f"Mode {mode_id} references non-existent file: {file_path}"
                
                # File should be valid JSON
                with open(full_path, 'r') as f:
                    data = json.load(f)
                    
                assert "shortcuts" in data, f"File {file_path} missing shortcuts key"
                
    def test_performance_with_large_dataset(self):
        """Test performance with full dataset"""
        import time
        
        start_time = time.time()
        lookup = ShortcutLookup(mode="full")
        load_time = time.time() - start_time
        
        # Should load in reasonable time (less than 1 second)
        assert load_time < 1.0, f"Loading full mode took too long: {load_time:.2f}s"
        
        # Should have loaded many shortcuts
        assert len(lookup.shortcuts) > 10, "Full mode should have many shortcuts"
        
        # Lookup should be fast
        start_time = time.time()
        for _ in range(100):
            lookup.lookup("Cmd+C")
        lookup_time = time.time() - start_time
        
        # 100 lookups should be very fast
        assert lookup_time < 0.1, f"100 lookups took too long: {lookup_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__])