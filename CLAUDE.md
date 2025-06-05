# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MemoKeys is a FastAPI + Vanilla JavaScript web application that tests users' knowledge of keyboard shortcuts through real-time keyboard detection. The current implementation supports Windows/Mac platform detection with actual shortcut interception.

## Development Commands

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
cd src && python main.py
# Server runs at http://127.0.0.1:8000

# Run tests (when implemented)
pytest

# Code formatting
black .
flake8 .
```

## Technical Architecture

### Technology Stack
- **FastAPI** for REST API backend with automatic OpenAPI documentation
- **Vanilla JavaScript** for frontend with real keyboard event handling
- **HTML/CSS** with CSS custom properties for dark/light theming
- **JSON files** for shortcut definitions with schema validation

### Why FastAPI + Vanilla JS (vs Streamlit)
The project migrated from Streamlit to FastAPI + Vanilla JS because:
- **Real keyboard detection**: Can intercept system shortcuts (Ctrl+C, Cmd+V) using `preventDefault()`
- **No page reloads**: Smooth, game-like experience with immediate feedback
- **Better UX**: Animations, themes, and responsive design
- **Educational value**: Demonstrates modern web development patterns
- **Scalability**: Clean API separation enables future mobile apps, React frontends, etc.

### Project Structure
```
src/main.py              # FastAPI backend
static/index.html        # Main application HTML
static/css/style.css     # Theming and responsive design
static/js/app.js         # Keyboard detection and application logic
data/shortcuts/system/   # JSON shortcut definitions
demos/streamlit_demo_1/  # Original Streamlit proof-of-concept
```

### Core Implementation Details

#### Keyboard Detection
```javascript
// Real-time keyboard event handling
document.addEventListener('keydown', (e) => {
    if (this.isListening) {
        if (e.ctrlKey || e.metaKey || e.altKey) {
            e.preventDefault(); // Intercept system shortcuts
        }
        // Build key combination (Ctrl+C, Cmd+V, etc.)
        this.detectKeyCombo(e);
    }
});
```

#### Platform Detection
```javascript
detectPlatform() {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Mac')) return 'mac';
    if (userAgent.includes('Win')) return 'windows';
    return 'windows'; // Default
}
```

#### API Endpoints
```python
@app.get("/api/shortcuts/{platform}")  # Get platform-specific shortcuts
@app.get("/")                          # Serve main application
@app.get("/api/health")               # Health check
```

## Data Architecture

### JSON Shortcut Schema
Shortcuts are defined in JSON files following a standardized schema:
```json
{
  "name": "Essential Windows Shortcuts",
  "platform": "windows",
  "shortcuts": [
    {
      "id": "copy",
      "action": "Copy selected text",
      "windows": "Ctrl+C",
      "mac": "Cmd+C",
      "category": "clipboard",
      "difficulty": "beginner"
    }
  ]
}
```

### Cross-Platform Support
- **Auto-detection**: JavaScript detects user's OS
- **Manual override**: Dropdown allows platform selection
- **Key mapping**: Backend serves appropriate shortcuts (Ctrl vs Cmd)

## User Experience Features

### Theming
- **Dark mode default** with light mode toggle
- **CSS custom properties** for consistent theming
- **Theme persistence** via localStorage

### Real-Time Feedback
- **Immediate validation** when shortcuts are pressed
- **Visual feedback** with color changes and animations
- **Audio cues** (extensible for future enhancement)
- **Progress tracking** with smooth progress bars

### Responsive Design
- **Mobile-friendly** layout with proper touch targets
- **Flexible grid** system for different screen sizes
- **Accessibility** considerations with focus styles

## Development Guidelines

### Adding New Shortcuts
1. Edit JSON files in `data/shortcuts/system/`
2. Follow the established schema structure
3. Include both Windows and Mac key combinations
4. Test cross-platform compatibility

### Frontend Development
- Use vanilla JavaScript for maximum compatibility
- Follow the existing class-based structure in `app.js`
- Maintain theme consistency with CSS custom properties
- Test keyboard detection across browsers

### Backend Development
- Follow FastAPI patterns with type hints
- Use Pydantic models for request/response validation
- Maintain RESTful API design principles
- Include proper error handling and status codes

## MVP Shortcut Set
Current test includes these essential shortcuts:
- Copy (Ctrl+C / Cmd+C)
- Paste (Ctrl+V / Cmd+V)
- Cut (Ctrl+X / Cmd+X)
- Undo (Ctrl+Z / Cmd+Z)
- Save (Ctrl+S / Cmd+S)

## Future Enhancement Areas
- **Spaced repetition** algorithm for personalized learning
- **Audio feedback** with distinctive sounds for each shortcut
- **Custom shortcut sets** for specific applications (VS Code, Photoshop, etc.)
- **User accounts** and progress tracking
- **Mobile app** using the same FastAPI backend

## Browser Compatibility Notes
- **System shortcuts**: Some shortcuts (Alt+Tab, Windows key) cannot be intercepted
- **Cross-browser testing**: Verify keyboard events work in Chrome, Firefox, Safari, Edge
- **Fallback options**: Provide manual input for accessibility
- **Security limitations**: Browsers prevent certain system-level shortcut capture

## Deployment Considerations
- **Static files**: Serve via FastAPI's StaticFiles or CDN
- **Environment variables**: Use for configuration management
- **CORS**: Configure for cross-origin requests if needed
- **Health checks**: `/api/health` endpoint for monitoring