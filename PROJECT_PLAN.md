# MemoKeys - Project Plan & Architecture

## Project Overview
MemoKeys is evolving from a simple 5-shortcut demo into a comprehensive, JSON-driven keyboard shortcut testing platform supporting multiple applications and operating systems.

## Current Status: Streamlit Demo 1
- ✅ Basic Streamlit interface with 5 hardcoded shortcuts  
- ✅ Keyboard detection proof-of-concept using JavaScript components
- ✅ Simple quiz flow with scoring and feedback
- ✅ Cross-platform shortcut normalization (basic)

## Architecture Vision

### Technology Stack
- **Backend**: Python with Streamlit for rapid prototyping
- **Frontend**: Streamlit components + custom JavaScript for keyboard detection
- **Data Layer**: JSON files for shortcut definitions
- **Schema**: JSON Schema for validation and consistency
- **Deployment**: Streamlit Cloud / Docker containers

### Project Structure
```
memokeys/
├── README.md
├── REQUIREMENTS.md
├── PROJECT_PLAN.md
├── CLAUDE.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── .env.example
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── app.py                    # Main Streamlit app
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── shortcut_loader.py    # JSON loading and validation
│   │   ├── test_engine.py        # Quiz logic and scoring
│   │   ├── keyboard_detector.py  # Keyboard event handling
│   │   └── platform_utils.py     # OS detection and normalization
│   ├── components/               # Streamlit custom components
│   │   ├── __init__.py
│   │   ├── keyboard_listener.py  # JavaScript keyboard component
│   │   └── shortcut_display.py   # Shortcut visualization
│   ├── data/                     # Data models and schemas
│   │   ├── __init__.py
│   │   ├── models.py             # Pydantic models
│   │   └── validators.py         # Custom validation logic
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── config.py             # Configuration management
│       └── helpers.py            # General helper functions
│
├── data/                         # Shortcut definitions
│   ├── schemas/                  # JSON schemas
│   │   └── shortcut-set.json
│   ├── shortcuts/                # Shortcut definition files
│   │   ├── system/
│   │   │   ├── windows-basic.json
│   │   │   ├── mac-basic.json
│   │   │   └── linux-basic.json
│   │   ├── browsers/
│   │   │   ├── chrome.json
│   │   │   ├── firefox.json
│   │   │   └── safari.json
│   │   ├── editors/
│   │   │   ├── vscode.json
│   │   │   ├── sublime.json
│   │   │   └── vim.json
│   │   └── productivity/
│   │       ├── slack.json
│   │       ├── notion.json
│   │       └── discord.json
│   └── examples/                 # Example shortcut sets
│       └── system-shortcuts-windows.json
│
├── docs/                         # Documentation
│   ├── api.md                    # API documentation
│   ├── schema-guide.md           # JSON schema guide
│   ├── contributing.md           # Contribution guidelines
│   └── deployment.md             # Deployment instructions
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_shortcut_loader.py   # Test shortcut loading
│   ├── test_test_engine.py       # Test quiz logic
│   └── data/                     # Test data files
│       └── test_shortcuts.json
│
├── scripts/                      # Utility scripts
│   ├── validate_shortcuts.py     # Validate all JSON files
│   ├── generate_docs.py          # Auto-generate documentation
│   └── setup_dev.py              # Development environment setup
│
└── demos/                        # Demo versions and prototypes
    ├── streamlit_demo_1/         # Current basic demo
    │   ├── app.py
    │   └── requirements.txt
    └── future_demos/             # Planned demo versions
```

## Development Phases

### Phase 1: Foundation & Structure (Current Sprint)
**Goals**: Establish proper project structure and core functionality

**Tasks**:
- ✅ Create requirements document
- ✅ Design JSON schema for shortcut definitions  
- ✅ Create example shortcut sets
- 🔄 Set up proper project structure (/src, /docs, etc.)
- 🔄 Create Python virtual environment
- 🔄 Move current demo to /demos/streamlit_demo_1/
- 🔄 Implement JSON shortcut loader with schema validation
- 🔄 Create Pydantic models for type safety
- 🔄 Basic test suite setup

**Deliverables**:
- Organized project structure
- JSON schema and validation
- Core data models
- Basic shortcut loading functionality

### Phase 2: Enhanced Demo (Streamlit Demo 2)
**Goals**: JSON-driven shortcut testing with multiple sets

**Tasks**:
- Load shortcuts from JSON files instead of hardcoded data
- Support multiple shortcut sets (system, browser, editor)
- Platform detection and appropriate shortcut display
- Category-based test selection
- Enhanced keyboard detection reliability
- Progress tracking across sessions

**Deliverables**:
- Multi-set shortcut testing
- Platform-aware shortcut display
- Persistent progress tracking
- Improved user experience

### Phase 3: Advanced Features
**Goals**: Production-ready testing platform

**Tasks**:
- Spaced repetition algorithm
- Adaptive difficulty adjustment
- Achievement system and badges
- Custom shortcut set creation
- Import/export functionality
- Performance analytics and insights

**Deliverables**:
- Intelligent learning system
- Gamification features
- User-generated content support
- Analytics dashboard

### Phase 4: Community & Ecosystem
**Goals**: Scale to support community contributions

**Tasks**:
- Community shortcut set repository
- Version control for shortcut definitions
- Collaborative editing of shortcut sets
- API for third-party integrations
- Plugin system for custom applications

**Deliverables**:
- Community platform
- API ecosystem
- Extensible architecture

## Technical Considerations

### JSON Schema Benefits
- **Validation**: Ensure all shortcut sets follow consistent structure
- **Documentation**: Schema serves as specification for contributors
- **Tooling**: Enable auto-completion and validation in editors
- **Evolution**: Version schema to support future enhancements

### Platform Detection Strategy
```python
# Automatic platform detection
platform = detect_platform()  # 'windows', 'mac', 'linux'

# Display appropriate shortcuts
if platform == 'mac':
    shortcut_text = shortcut.mac or shortcut.windows
elif platform == 'linux':  
    shortcut_text = shortcut.linux or shortcut.windows
else:
    shortcut_text = shortcut.windows
```

### Keyboard Detection Challenges
- **Browser limitations**: Some shortcuts can't be intercepted
- **Platform differences**: Key codes vary between OS
- **Accessibility**: Need fallback for users who can't use keyboard
- **Security**: Browsers prevent certain system shortcut capture

### Data Management
- **Local files**: JSON files in repository for core shortcuts
- **User data**: Browser localStorage for progress and custom sets
- **Validation**: Real-time schema validation on JSON loading
- **Caching**: Efficient loading of large shortcut sets

## Success Metrics

### Development Metrics
- **Code coverage**: >80% test coverage
- **JSON validation**: 100% schema compliance
- **Platform support**: Windows, Mac, Linux compatibility
- **Load performance**: <2s initial load, <500ms shortcut set switching

### User Experience Metrics  
- **Completion rate**: >70% of started tests completed
- **Accuracy improvement**: Measurable score increases over time
- **Retention**: Users returning for multiple sessions
- **Contribution**: Community-created shortcut sets

## Risk Management

### Technical Risks
- **Keyboard detection reliability**: Fallback to manual input
- **Cross-platform inconsistencies**: Extensive testing matrix
- **Performance with large datasets**: Lazy loading and caching
- **Browser compatibility**: Progressive enhancement approach

### Project Risks
- **Scope creep**: Phased delivery with MVP validation
- **Complexity management**: Clear separation of concerns
- **Community adoption**: Early engagement and feedback loops
- **Maintenance burden**: Automated testing and validation

## Next Steps (Immediate)
1. Set up proper project structure with virtual environment
2. Move current demo to /demos/streamlit_demo_1/
3. Implement JSON shortcut loader with Pydantic models
4. Create basic test suite for core functionality
5. Validate example shortcut sets against schema
6. Document API and contribution guidelines