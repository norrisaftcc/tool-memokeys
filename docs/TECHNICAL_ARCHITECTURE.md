# Technical Architecture

## Technology Stack
- **FastAPI** for REST API backend with automatic OpenAPI documentation
- **Vanilla JavaScript** for frontend with real keyboard event handling
- **HTML/CSS** with CSS custom properties for dark/light theming
- **JSON files** for shortcut definitions with schema validation

## Why FastAPI + Vanilla JS (vs Streamlit)
The project migrated from Streamlit to FastAPI + Vanilla JS because:
- **Real keyboard detection**: Can intercept system shortcuts (Ctrl+C, Cmd+V) using `preventDefault()`
- **No page reloads**: Smooth, game-like experience with immediate feedback
- **Better UX**: Animations, themes, and responsive design
- **Educational value**: Demonstrates modern web development patterns
- **Scalability**: Clean API separation enables future mobile apps, React frontends, etc.

## Project Structure
```
src/main.py              # FastAPI backend
static/index.html        # Main application HTML
static/css/style.css     # Theming and responsive design
static/js/app.js         # Keyboard detection and application logic
data/shortcuts/system/   # JSON shortcut definitions
demos/streamlit_demo_1/  # Original Streamlit proof-of-concept
```

## Core Implementation Details

### Keyboard Detection
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

### Platform Detection
```javascript
detectPlatform() {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Mac')) return 'mac';
    if (userAgent.includes('Win')) return 'windows';
    return 'windows'; // Default
}
```

### API Endpoints
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