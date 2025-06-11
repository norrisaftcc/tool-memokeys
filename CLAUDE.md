# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with MemoKeys.

## Project Overview

MemoKeys is a FastAPI + Vanilla JavaScript web application that tests users' knowledge of keyboard shortcuts through real-time keyboard detection. It supports Windows/Mac platform detection with actual shortcut interception.

## Quick Start

```bash
# Setup and run
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd src && python main.py  # Runs at http://127.0.0.1:8000
```

## Key Commands

- **Lint/Format**: `black .` and `flake8 .`
- **Tests**: `pytest` (when implemented)

## Project Structure

```
src/main.py              # FastAPI backend
static/index.html        # Main application
static/js/app.js         # Keyboard detection logic
data/shortcuts/system/   # JSON shortcut definitions
```

## Core Features

- **Real keyboard detection** with `preventDefault()` for system shortcuts
- **Cross-platform support** (Windows/Mac auto-detection)
- **Dark/light themes** with CSS custom properties
- **Immediate feedback** with visual and progress tracking

## MVP Shortcuts

- Copy (Ctrl+C / Cmd+C)
- Paste (Ctrl+V / Cmd+V)
- Cut (Ctrl+X / Cmd+X)
- Undo (Ctrl+Z / Cmd+Z)
- Save (Ctrl+S / Cmd+S)

## Documentation

For detailed information, see:
- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md) - Stack details, implementation, data schema
- [Development Guide](docs/DEVELOPMENT_GUIDE.md) - Guidelines, commands, deployment notes

## Future Enhancements

- Spaced repetition algorithm
- Audio feedback system
- Custom shortcut sets (VS Code, Photoshop, etc.)
- User accounts and progress tracking
- Mobile app support