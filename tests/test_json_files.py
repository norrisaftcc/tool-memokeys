#!/usr/bin/env python3
"""
Tests for JSON file structure and content validation
"""

import pytest
import json
from pathlib import Path
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestJSONFiles:
    """Test JSON file structure and content"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.shortcuts_dir = Path("data/shortcuts")
        
    def test_shortcuts_directory_exists(self):
        """Test that shortcuts directory exists"""
        assert self.shortcuts_dir.exists()
        assert self.shortcuts_dir.is_dir()
        
    def test_modes_file_structure(self):
        """Test modes.json file structure"""
        modes_file = self.shortcuts_dir / "modes.json"
        assert modes_file.exists()
        
        with open(modes_file, 'r') as f:
            data = json.load(f)
            
        # Should have modes key
        assert "modes" in data
        assert isinstance(data["modes"], dict)
        
        # Each mode should have required fields
        for mode_id, mode_info in data["modes"].items():
            assert isinstance(mode_id, str)
            assert isinstance(mode_info, dict)
            
            required_fields = ["name", "description", "files"]
            for field in required_fields:
                assert field in mode_info, f"Mode '{mode_id}' missing field '{field}'"
                
            assert isinstance(mode_info["files"], list)
            assert len(mode_info["files"]) > 0
            
    def test_shortcut_files_exist(self):
        """Test that all files referenced in modes exist"""
        modes_file = self.shortcuts_dir / "modes.json"
        with open(modes_file, 'r') as f:
            data = json.load(f)
            
        for mode_id, mode_info in data["modes"].items():
            for file_path in mode_info["files"]:
                full_path = self.shortcuts_dir / file_path
                assert full_path.exists(), f"File {file_path} referenced in mode '{mode_id}' does not exist"
                
    def test_shortcut_file_structure(self):
        """Test structure of individual shortcut files"""
        # Get all JSON files except modes.json
        json_files = [f for f in self.shortcuts_dir.rglob("*.json") if f.name != "modes.json"]
        
        assert len(json_files) > 0, "No shortcut JSON files found"
        
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            # Should have basic metadata
            assert "name" in data, f"File {json_file} missing 'name' field"
            assert "shortcuts" in data, f"File {json_file} missing 'shortcuts' field"
            assert isinstance(data["shortcuts"], list), f"File {json_file} 'shortcuts' should be a list"
            
            # Test each shortcut
            for i, shortcut in enumerate(data["shortcuts"]):
                assert isinstance(shortcut, dict), f"File {json_file} shortcut {i} should be a dict"
                
                required_fields = ["id", "action"]
                for field in required_fields:
                    assert field in shortcut, f"File {json_file} shortcut {i} missing field '{field}'"
                    
                # Should have at least one platform key
                platform_keys = ["mac", "windows", "linux"]
                has_platform = any(key in shortcut for key in platform_keys)
                assert has_platform, f"File {json_file} shortcut {i} missing platform keys"
                
    def test_mac_shortcut_format(self):
        """Test Mac shortcut key combination format"""
        json_files = [f for f in self.shortcuts_dir.rglob("*.json") if f.name != "modes.json"]
        
        valid_modifiers = {"cmd", "command", "ctrl", "control", "alt", "option", "shift"}
        valid_keys = set("abcdefghijklmnopqrstuvwxyz0123456789")
        valid_keys.update({"space", "enter", "return", "tab", "escape", "esc", 
                          "backspace", "delete", "up", "down", "left", "right",
                          "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
                          "/", "-", "=", "[", "]", "\\", ";", "'", ",", ".", "`"})
        
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            for shortcut in data["shortcuts"]:
                if "mac" in shortcut:
                    mac_combo = shortcut["mac"].lower()
                    
                    # Should not be empty
                    assert mac_combo.strip(), f"Empty mac shortcut in {json_file}: {shortcut}"
                    
                    # Split by + and validate parts
                    parts = [part.strip() for part in mac_combo.split("+")]
                    assert len(parts) >= 1, f"Invalid mac shortcut format in {json_file}: {shortcut['mac']}"
                    
                    # Last part should be a key, others should be modifiers
                    for part in parts[:-1]:
                        assert part in valid_modifiers, f"Invalid modifier '{part}' in {json_file}: {shortcut['mac']}"
                        
                    # Last part should be a valid key
                    last_part = parts[-1]
                    assert last_part in valid_keys, f"Invalid key '{last_part}' in {json_file}: {shortcut['mac']}"
                    
    def test_no_duplicate_shortcuts(self):
        """Test that there are no duplicate shortcut IDs within files"""
        json_files = [f for f in self.shortcuts_dir.rglob("*.json") if f.name != "modes.json"]
        
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            ids = [shortcut["id"] for shortcut in data["shortcuts"]]
            unique_ids = set(ids)
            
            assert len(ids) == len(unique_ids), f"Duplicate shortcut IDs found in {json_file}"
            
    def test_basic_shortcuts_exist(self):
        """Test that basic essential shortcuts exist"""
        # These are shortcuts we expect to be in the basic mac shortcuts
        expected_shortcuts = {
            "cmd+c": ["copy", "copy text", "copy selection"],
            "cmd+v": ["paste", "paste text", "paste clipboard"],
            "cmd+z": ["undo", "undo last action"],
            "cmd+space": ["spotlight", "open spotlight", "spotlight search"]
        }
        
        # Load basic mac shortcuts
        basic_file = self.shortcuts_dir / "system" / "mac-basics.json"
        assert basic_file.exists()
        
        with open(basic_file, 'r') as f:
            data = json.load(f)
            
        # Create lookup of normalized shortcuts to actions
        shortcuts = {}
        for shortcut in data["shortcuts"]:
            if "mac" in shortcut:
                normalized = shortcut["mac"].lower().replace(" ", "").replace("command", "cmd")
                shortcuts[normalized] = shortcut["action"].lower()
                
        # Check that expected shortcuts exist
        for combo, expected_actions in expected_shortcuts.items():
            assert combo in shortcuts, f"Expected basic shortcut {combo} not found"
            
            action = shortcuts[combo]
            action_matches = any(expected in action for expected in expected_actions)
            assert action_matches, f"Shortcut {combo} has unexpected action: {action}"


if __name__ == "__main__":
    pytest.main([__file__])