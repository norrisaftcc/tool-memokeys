# Development Guide

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