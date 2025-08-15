# MemoKeys MVP Specification

## Platform: macOS Only

## Core MVP Requirements

### Must Have (Week 1)
1. **Floating Overlay Window (macOS Native)**
   - NSWindow with NSWindowLevel.floating
   - Always on top functionality
   - Draggable & resizable
   - Semi-transparent background
   - Minimal UI footprint
   - Quick hide/show hotkey (Cmd+Shift+K)

2. **Real-Time Keyboard Detection**
   - macOS Accessibility API for global key capture
   - Show keys as they're pressed
   - Visual feedback for correct/incorrect
   - Support Cmd/Option/Control/Shift modifiers
   - Clear visual distinction for modifiers

3. **5 Essential Mac Shortcuts**
   - Copy (Cmd+C)
   - Paste (Cmd+V)
   - Cut (Cmd+X)
   - Undo (Cmd+Z)
   - Save (Cmd+S)

4. **Simple Practice Mode**
   - Random shortcut prompts
   - Success/fail feedback
   - Basic score counter
   - Reset button

### Nice to Have (Week 2)
- Platform auto-detection
- Dark/light mode toggle
- Keyboard sound effects
- Session statistics
- Shortcut hint after 3 seconds

### Not in MVP
- User accounts
- Cloud sync
- Custom shortcuts
- Multiple shortcut sets
- Analytics dashboard
- Team features

## Technical Approach

### Native macOS App (Swift or Python)
```python
# Using PyObjC for native macOS window
from AppKit import NSWindow, NSWindowLevel, NSApp
from AppKit import NSApplicationActivationPolicyAccessory

# Create floating window
window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    ((100, 100), (400, 150)),
    NSWindowStyleMaskTitled | NSWindowStyleMaskResizable,
    NSBackingStoreBuffered,
    False
)
window.setLevel_(NSWindowLevel.floating)
window.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
```

### Build on Existing Code
- We already have `hotkey_panel_proto/native_app.py` 
- Uses PyObjC for native macOS integration
- Has keyboard monitoring with pynput
- Just needs overlay window enhancement

## UI Mockup
```
┌─────────────────────────────────┐
│ MemoKeys          [_][□][x] │
├─────────────────────────────────┤
│                                 │
│     Press: Cmd + C              │
│                                 │
│     [⌘] + [C]                   │
│                                 │
│     Score: 8/10    [Reset]      │
└─────────────────────────────────┘
```

## Success Criteria
- User can practice 5 shortcuts
- Overlay stays on top of other windows
- Keyboard detection works reliably
- Visual feedback is immediate (<50ms)
- Can be used while working in other apps

## Timeline
- Day 1: Enhance existing native_app.py with floating overlay
- Day 2: Improve keyboard detection & visual feedback
- Day 3: Add practice mode + scoring
- Day 4: Polish + testing + Accessibility permissions

## Launch Checklist
- [ ] Overlay always stays on top (NSWindowLevel.floating)
- [ ] All 5 Mac shortcuts work correctly  
- [ ] Visual feedback is clear and immediate
- [ ] Window is draggable and resizable
- [ ] Quick hide/show works (Cmd+Shift+K)
- [ ] macOS Accessibility permissions handled gracefully
- [ ] No memory leaks
- [ ] < 20MB app size
- [ ] Works on macOS 12+ (Monterey and newer)