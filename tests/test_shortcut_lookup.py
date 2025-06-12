#!/usr/bin/env python3
"""
Tests for ShortcutLookup functionality
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys
import os

# Add the parent directory to sys.path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hotkey_panel_proto.hotkey_display import ShortcutLookup


class TestShortcutLookup:
    """Test the ShortcutLookup class functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.shortcuts_dir = Path(self.temp_dir) / "shortcuts"
        self.shortcuts_dir.mkdir()
        
        # Create test JSON files
        self.create_test_files()
        
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def create_test_files(self):
        """Create test shortcut files"""
        # Basic system shortcuts
        system_dir = self.shortcuts_dir / "system"
        system_dir.mkdir()
        
        basic_shortcuts = {
            "name": "Test Basic",
            "shortcuts": [
                {"id": "copy", "action": "Copy", "mac": "Cmd+C"},
                {"id": "paste", "action": "Paste", "mac": "Cmd+V"},
                {"id": "undo", "action": "Undo", "mac": "Cmd+Z"}
            ]
        }
        
        with open(system_dir / "basic.json", "w") as f:
            json.dump(basic_shortcuts, f)
            
        # VSCode shortcuts
        editors_dir = self.shortcuts_dir / "editors"
        editors_dir.mkdir()
        
        vscode_shortcuts = {
            "name": "Test VSCode",
            "shortcuts": [
                {"id": "command-palette", "action": "Command Palette", "mac": "Cmd+Shift+P"},
                {"id": "quick-open", "action": "Quick Open", "mac": "Cmd+P"},
                {"id": "toggle-comment", "action": "Toggle Comment", "mac": "Cmd+/"}
            ]
        }
        
        with open(editors_dir / "vscode.json", "w") as f:
            json.dump(vscode_shortcuts, f)
            
        # Modes configuration
        modes_config = {
            "modes": {
                "basic": {
                    "name": "Basic Test",
                    "description": "Basic shortcuts only",
                    "files": ["system/basic.json"]
                },
                "vscode": {
                    "name": "VSCode Test",
                    "description": "Basic + VSCode shortcuts",
                    "files": ["system/basic.json", "editors/vscode.json"]
                }
            }
        }
        
        with open(self.shortcuts_dir / "modes.json", "w") as f:
            json.dump(modes_config, f)
    
    def test_normalize_shortcut(self):
        """Test shortcut normalization"""
        lookup = ShortcutLookup()
        
        # Test basic normalization
        assert lookup.normalize_shortcut("Cmd+C") == "cmd+c"
        assert lookup.normalize_shortcut("cmd+c") == "cmd+c"
        
        # Test modifier ordering
        assert lookup.normalize_shortcut("Shift+Cmd+P") == "cmd+shift+p"
        assert lookup.normalize_shortcut("Cmd+Shift+P") == "cmd+shift+p"
        
        # Test space removal
        assert lookup.normalize_shortcut("Cmd + C") == "cmd+c"
        
        # Test alternative modifier names
        assert lookup.normalize_shortcut("Command+C") == "cmd+c"
        assert lookup.normalize_shortcut("Option+C") == "alt+c"
        assert lookup.normalize_shortcut("Control+C") == "ctrl+c"
    
    def test_load_all_shortcuts(self):
        """Test loading all shortcuts without mode"""
        # Temporarily patch the shortcuts directory
        original_init = ShortcutLookup.__init__
        
        def patched_init(self, mode=None):
            self.shortcuts = {}
            self.mode = mode
            self.shortcuts_dir = Path(self.temp_dir) / "shortcuts"
            self.load_shortcuts()
            
        ShortcutLookup.__init__ = patched_init
        
        try:
            lookup = ShortcutLookup()
            
            # Should have loaded all shortcuts
            assert "cmd+c" in lookup.shortcuts
            assert lookup.shortcuts["cmd+c"] == "Copy"
            
            assert "cmd+shift+p" in lookup.shortcuts  
            assert lookup.shortcuts["cmd+shift+p"] == "Command Palette"
            
            # Should have 6 total shortcuts (3 basic + 3 vscode)
            assert len(lookup.shortcuts) == 6
            
        finally:
            ShortcutLookup.__init__ = original_init
    
    def test_load_mode_shortcuts(self):
        """Test loading shortcuts for specific mode"""
        original_init = ShortcutLookup.__init__
        
        def patched_init(self, mode=None):
            self.shortcuts = {}
            self.mode = mode
            self.shortcuts_dir = Path(self.temp_dir) / "shortcuts"
            self.load_shortcuts()
            
        ShortcutLookup.__init__ = patched_init
        
        try:
            # Test basic mode
            lookup_basic = ShortcutLookup(mode="basic")
            assert len(lookup_basic.shortcuts) == 3
            assert "cmd+c" in lookup_basic.shortcuts
            assert "cmd+shift+p" not in lookup_basic.shortcuts
            
            # Test vscode mode
            lookup_vscode = ShortcutLookup(mode="vscode")
            assert len(lookup_vscode.shortcuts) == 6
            assert "cmd+c" in lookup_vscode.shortcuts
            assert "cmd+shift+p" in lookup_vscode.shortcuts
            
        finally:
            ShortcutLookup.__init__ = original_init
    
    def test_lookup_functionality(self):
        """Test shortcut lookup with different formats"""
        original_init = ShortcutLookup.__init__
        
        def patched_init(self, mode=None):
            self.shortcuts = {}
            self.mode = mode
            self.shortcuts_dir = Path(self.temp_dir) / "shortcuts"
            self.load_shortcuts()
            
        ShortcutLookup.__init__ = patched_init
        
        try:
            lookup = ShortcutLookup()
            
            # Test exact match
            assert lookup.lookup("Cmd+C") == "Copy"
            assert lookup.lookup("cmd+c") == "Copy"
            
            # Test with icons (should convert to text)
            assert lookup.lookup("⌘+C") == "Copy"
            assert lookup.lookup("⌘+⇧+P") == "Command Palette"
            
            # Test non-existent shortcut
            assert lookup.lookup("Cmd+X") is None
            
        finally:
            ShortcutLookup.__init__ = original_init
    
    def test_get_available_modes(self):
        """Test getting available modes"""
        original_init = ShortcutLookup.__init__
        
        def patched_init(self, mode=None):
            self.shortcuts = {}
            self.mode = mode
            self.shortcuts_dir = Path(self.temp_dir) / "shortcuts"
            self.load_shortcuts()
            
        ShortcutLookup.__init__ = patched_init
        
        try:
            lookup = ShortcutLookup()
            modes = lookup.get_available_modes()
            
            assert "basic" in modes
            assert "vscode" in modes
            assert modes["basic"]["name"] == "Basic Test"
            assert modes["vscode"]["description"] == "Basic + VSCode shortcuts"
            
        finally:
            ShortcutLookup.__init__ = original_init
    
    def test_invalid_mode(self):
        """Test handling of invalid mode"""
        original_init = ShortcutLookup.__init__
        
        def patched_init(self, mode=None):
            self.shortcuts = {}
            self.mode = mode
            self.shortcuts_dir = Path(self.temp_dir) / "shortcuts"
            self.load_shortcuts()
            
        ShortcutLookup.__init__ = patched_init
        
        try:
            lookup = ShortcutLookup(mode="nonexistent")
            # Should have no shortcuts loaded
            assert len(lookup.shortcuts) == 0
            
        finally:
            ShortcutLookup.__init__ = original_init


if __name__ == "__main__":
    pytest.main([__file__])