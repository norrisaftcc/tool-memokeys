#!/usr/bin/env python3
"""Test the modes system without GUI dependencies"""

import json
from pathlib import Path

def test_modes():
    shortcuts_dir = Path("data/shortcuts")
    modes_file = shortcuts_dir / "modes.json"
    
    try:
        with open(modes_file, "r") as f:
            data = json.load(f)
            modes = data.get("modes", {})
            
        print("Available KeyCast modes:")
        print("=" * 40)
        for mode_id, mode_info in modes.items():
            print(f"{mode_id:12} - {mode_info['name']}")
            print(f"{'':14} {mode_info['description']}")
            print(f"{'':14} Files: {', '.join(mode_info['files'])}")
            print()
            
        # Test loading shortcuts for a mode
        print("Testing 'vscode' mode shortcut loading:")
        print("-" * 40)
        
        vscode_mode = modes.get("vscode", {})
        total_shortcuts = 0
        
        for file_path in vscode_mode.get("files", []):
            full_path = shortcuts_dir / file_path
            try:
                with open(full_path, "r") as f:
                    data = json.load(f)
                    if "shortcuts" in data:
                        shortcuts = [s for s in data["shortcuts"] if "mac" in s and "action" in s]
                        print(f"{file_path}: {len(shortcuts)} shortcuts")
                        total_shortcuts += len(shortcuts)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        print(f"\nTotal shortcuts in vscode mode: {total_shortcuts}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_modes()