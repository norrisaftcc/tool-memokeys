# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MemoKeys is a Python Streamlit web application that tests users' knowledge of keyboard shortcuts through an interactive testing interface. The MVP focuses on 5 essential Windows shortcuts with a streamlined quiz-based approach.

## Development Commands

```bash
# Setup
pip install -r requirements.txt

# Run development server
streamlit run app.py

# Run tests (when implemented)
pytest

# Code formatting
black .
flake8 .
```

## Technical Architecture

### Technology Stack
- **Streamlit** for web interface and state management
- **Python** for application logic
- **Session state** for maintaining quiz progress

### Implementation Approach
Since Streamlit runs in a browser and cannot intercept system keyboard shortcuts, the application uses:
- **Text input fields** for users to type their shortcut answers
- **Multiple choice questions** for shortcut recognition
- **Interactive widgets** for engaging quiz experience
- **Session state** to track progress and scoring

### Application State Structure
```python
# Key session state variables
if 'test_active' not in st.session_state:
    st.session_state.test_active = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'test_completed' not in st.session_state:
    st.session_state.test_completed = False
```

### MVP Shortcut Set
Test these 5 fundamental shortcuts:
- Copy (Ctrl + C)
- Paste (Ctrl + V)
- Cut (Ctrl + X)
- Undo (Ctrl + Z)
- Redo (Ctrl + Y)

## Implementation Guidelines

### Application Structure
- **Main App**: `app.py` contains all Streamlit logic
- **Quiz Data**: Dictionary or class containing shortcut questions and answers
- **State Management**: Use `st.session_state` for maintaining quiz progress

### User Flow
1. Welcome screen with start button
2. Sequential shortcut questions with input fields
3. Immediate feedback after each answer
4. Progress indicator showing current question
5. Final score screen with retry option

### Quiz Question Types
- **Text Input**: "What shortcut copies selected text?" → User types "Ctrl+C"
- **Multiple Choice**: "Which shortcut undoes the last action?" → A) Ctrl+Z B) Ctrl+Y C) Ctrl+X
- **Description Match**: Show shortcut, ask what it does

## Development Notes

- Use `st.rerun()` to refresh the app after state changes
- Implement answer validation with case-insensitive matching
- Use Streamlit's built-in styling for consistent UI
- Keep session state minimal and well-organized
- Add progress bars and success/error messages for better UX