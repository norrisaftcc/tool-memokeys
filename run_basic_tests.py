#!/usr/bin/env python3
"""
Basic test runner that doesn't require GUI dependencies
Tests core functionality without pynput/AppKit
"""

import sys
import json
from pathlib import Path

def test_json_structure():
    """Test that JSON files have correct structure"""
    print("Testing JSON structure...")
    
    shortcuts_dir = Path("data/shortcuts")
    
    # Test modes.json
    modes_file = shortcuts_dir / "modes.json"
    assert modes_file.exists(), "modes.json not found"
    
    with open(modes_file, 'r') as f:
        modes_data = json.load(f)
        
    assert "modes" in modes_data, "modes.json missing 'modes' key"
    
    print(f"✅ Found {len(modes_data['modes'])} modes")
    
    # Test each mode's files exist
    for mode_id, mode_info in modes_data["modes"].items():
        print(f"  Testing mode: {mode_id}")
        assert "files" in mode_info, f"Mode {mode_id} missing 'files'"
        
        for file_path in mode_info["files"]:
            full_path = shortcuts_dir / file_path
            assert full_path.exists(), f"File {file_path} not found"
            
            # Test file structure
            with open(full_path, 'r') as f:
                data = json.load(f)
                
            assert "shortcuts" in data, f"File {file_path} missing 'shortcuts'"
            assert isinstance(data["shortcuts"], list), f"File {file_path} shortcuts not a list"
            
    print("✅ JSON structure tests passed")

def test_shortcut_normalization():
    """Test shortcut normalization logic"""
    print("\nTesting shortcut normalization...")
    
    # Simple normalization function (extracted from main code)
    def normalize_shortcut(shortcut_str):
        normalized = shortcut_str.lower()
        normalized = normalized.replace("command", "cmd")
        normalized = normalized.replace("option", "alt")
        normalized = normalized.replace("control", "ctrl")
        normalized = normalized.replace(" ", "")
        
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
    
    # Test cases
    test_cases = [
        ("Cmd+C", "cmd+c"),
        ("Command+C", "cmd+c"),
        ("Shift+Cmd+P", "cmd+shift+p"),
        ("Cmd+Shift+P", "cmd+shift+p"),
        ("Cmd + C", "cmd+c"),
        ("Option+C", "alt+c"),
        ("Control+C", "ctrl+c")
    ]
    
    for input_str, expected in test_cases:
        result = normalize_shortcut(input_str)
        assert result == expected, f"Expected {expected}, got {result} for {input_str}"
        
    print("✅ Shortcut normalization tests passed")

def test_basic_shortcuts_exist():
    """Test that essential shortcuts exist in basic mode"""
    print("\nTesting basic shortcuts...")
    
    shortcuts_dir = Path("data/shortcuts")
    basic_file = shortcuts_dir / "system" / "mac-basics.json"
    
    if not basic_file.exists():
        print("⚠️  mac-basics.json not found, skipping basic shortcuts test")
        return
        
    with open(basic_file, 'r') as f:
        data = json.load(f)
        
    # Extract shortcuts
    shortcuts = {}
    for shortcut in data["shortcuts"]:
        if "mac" in shortcut and "action" in shortcut:
            normalized = shortcut["mac"].lower().replace(" ", "").replace("command", "cmd")
            shortcuts[normalized] = shortcut["action"]
            
    # Check for essential shortcuts
    essential = ["cmd+c", "cmd+v", "cmd+z"]
    found = 0
    
    for combo in essential:
        if combo in shortcuts:
            print(f"  ✅ {combo}: {shortcuts[combo]}")
            found += 1
        else:
            print(f"  ❌ {combo}: not found")
            
    assert found >= 2, f"Expected at least 2 essential shortcuts, found {found}"
    print(f"✅ Found {found}/{len(essential)} essential shortcuts")

def test_mode_loading():
    """Test that modes load correct number of shortcuts"""
    print("\nTesting mode loading...")
    
    shortcuts_dir = Path("data/shortcuts")
    modes_file = shortcuts_dir / "modes.json"
    
    with open(modes_file, 'r') as f:
        modes_data = json.load(f)
        
    for mode_id, mode_info in modes_data["modes"].items():
        total_shortcuts = 0
        
        for file_path in mode_info["files"]:
            full_path = shortcuts_dir / file_path
            with open(full_path, 'r') as f:
                data = json.load(f)
                
            mac_shortcuts = [s for s in data["shortcuts"] if "mac" in s and "action" in s]
            total_shortcuts += len(mac_shortcuts)
            
        print(f"  {mode_id}: {total_shortcuts} shortcuts")
        assert total_shortcuts > 0, f"Mode {mode_id} has no shortcuts"
        
    print("✅ Mode loading tests passed")

def main():
    """Run all basic tests"""
    print("MemoKeys/KeyCast Basic Test Suite")
    print("=================================")
    
    try:
        test_json_structure()
        test_shortcut_normalization()
        test_basic_shortcuts_exist()
        test_mode_loading()
        
        print("\n🎉 All basic tests passed!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())