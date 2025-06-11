# Changelog

All notable changes to MemoKeys will be documented in this file.

## [v1.1.0] - 2025-06-11 - Sprint 1 Complete

### 🔒 Security
- **BREAKING**: Fixed critical path traversal vulnerability in file path construction
- Added comprehensive input validation using Pydantic enums (Platform, Difficulty)
- Implemented security logging for monitoring potential attacks
- Added proper UTF-8 encoding for all file operations
- Validated all user inputs against known safe patterns

### 🐛 Bug Fixes
- Fixed legacy endpoint bug that always returned Windows shortcuts regardless of platform
- Now correctly routes: Mac users → mac-basics, Windows users → system-shortcuts-windows
- Added proper error handling for malformed JSON files
- Fixed missing file encoding specifications

### ✨ Features
- **NEW**: Inline error messages replace all blocking alert() dialogs
- **NEW**: Auto-dismissing error messages with close buttons
- **NEW**: Comprehensive error handling for all API calls
- **NEW**: Structured logging throughout the application
- **NEW**: Enhanced type safety with Pydantic models

### 🎨 UI/UX
- Replaced all browser alert() dialogs with elegant inline error messages
- Added CSS animations for error message appearance
- Implemented ARIA accessibility attributes (role="alert", aria-live="polite")
- Added responsive error message design with close functionality
- Auto-hide errors after 10 seconds with manual close option

### 🛠️ Technical
- Enhanced API endpoints with proper HTTP status codes
- Added comprehensive exception handling with specific error types
- Implemented proper validation for shortcut set IDs
- Added detailed error logging for debugging and monitoring
- Code formatted with Black for consistency

### 📝 Documentation
- Updated TECHNICAL_ARCHITECTURE.md with security features
- Enhanced API endpoint documentation
- Updated sprint plan with completion status
- Added comprehensive changelog

---

## [v1.0.0] - 2025-06-11 - Multiple Shortcut Sets

### ✨ Features
- **NEW**: Multiple shortcut set support with dynamic discovery
- **NEW**: 9 different shortcut sets across 4 categories (system, browsers, editors, productivity)
- **NEW**: Platform-specific shortcut filtering (Windows/Mac)
- **NEW**: Visual shortcut set selection interface
- **NEW**: Enhanced VS Code shortcuts (expanded from 5 to 25 shortcuts)

### 📁 Content
- Added Mac Basics shortcuts (15 essential macOS shortcuts)
- Added Windows Basics shortcuts (20 essential Windows shortcuts)  
- Added Chrome Browser shortcuts (5 essential browser shortcuts)
- Added VS Code Editor shortcuts (25 comprehensive shortcuts)
- Added Slack Productivity shortcuts (5 workflow shortcuts)
- Added Adobe Creative Suite shortcuts (25 shortcuts for Photoshop, Illustrator, Premiere)

### 🏗️ Architecture
- Refactored backend to support dynamic shortcut set loading
- Added new API endpoints: `/api/shortcut-sets` and `/api/shortcuts/{set_id}/{platform}`
- Implemented Pydantic models for type safety
- Added comprehensive JSON schema validation

### 📖 Documentation
- Refactored CLAUDE.md for clarity (reduced from 179 to 60 lines)
- Created separate TECHNICAL_ARCHITECTURE.md and DEVELOPMENT_GUIDE.md
- Added comprehensive code review documentation
- Created detailed sprint planning documentation

---

## [v0.1.0] - Initial MVP

### ✨ Features
- Basic keyboard shortcut testing with 5 system shortcuts
- Real-time keyboard detection with preventDefault() for system shortcuts
- Cross-platform support (Windows/Mac auto-detection)
- Dark/light theme toggle with persistence
- Three-screen flow: Welcome → Test → Results
- Score tracking and detailed results

### 🎨 UI/UX
- Responsive design with CSS custom properties
- Visual feedback for correct/incorrect answers
- Progress tracking with smooth animations
- Theme persistence via localStorage

### 🛠️ Technical
- FastAPI backend with automatic OpenAPI documentation
- Vanilla JavaScript frontend for maximum compatibility
- Static file serving
- JSON-based shortcut definitions