# CLAUDE.md

MemoKeys: Keyboard shortcut practice tool with web and native interfaces.

## Quick Start

```bash
# Web app
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd src && python main.py  # http://127.0.0.1:8000

# Native app (macOS only, requires Accessibility permissions)
pip install -r hotkey_panel_proto/requirements.txt
python hotkey_panel_proto/native_app.py
```

## Commands
- **Lint**: `black .` and `flake8 .`
- **Test**: `pytest` (when implemented)

## Key Files
- `src/main.py` - FastAPI backend
- `static/js/app.js` - Web keyboard detection
- `hotkey_panel_proto/` - Native macOS keyboard detection prototype
- `data/shortcuts/` - JSON shortcut definitions

## Development Focus
- Real keyboard shortcut detection
- Cross-platform support (web) / macOS (native)
- Immediate visual feedback
- MVP: 5 basic shortcuts (Copy/Paste/Cut/Undo/Save)