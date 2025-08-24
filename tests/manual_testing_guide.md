# Manual Testing Guide for Hotkey Filtering Improvements (Issue #2)

## Overview
This guide provides comprehensive manual testing procedures for validating the keyboard filtering improvements implemented in the Swift overlay (`prototypes/hotkey-overlay.swift`).

## Pre-Testing Setup

### Prerequisites
1. **macOS System** - Required for Swift overlay
2. **Accessibility Permissions** - Grant when prompted by the system
3. **Clean Environment** - Close other applications that might interfere with keyboard monitoring

### Launch the Application
```bash
cd /Users/norrisa/Documents/dev/github/tool-memokeys
swift prototypes/hotkey-overlay.swift
```

Expected output:
```
Hotkey overlay is running! Press Ctrl+C in terminal to quit.
The overlay will show in the bottom-right corner of your screen.
NOTE: You'll need to grant Accessibility permissions when prompted.
```

## Test Scenarios

### 1. Primary Filtering Tests (CRITICAL)

#### Test 1.1: Single Letter Filtering
**Objective**: Verify single letters without modifiers are filtered out

**Test Steps**:
1. Press individual keys: `a`, `b`, `c`, `1`, `2`, `3`, `z`
2. Observe overlay display

**Expected Result**: 
- ✅ No display should appear for single letter presses
- ✅ Overlay should remain empty or show "Ready..."

**Actual Result**: _[To be filled during testing]_

#### Test 1.2: Command Key Combinations
**Objective**: Verify Command (⌘) combinations are displayed

**Test Steps**:
1. Press `⌘+C`
2. Press `⌘+V` 
3. Press `⌘+S`
4. Press `⌘+A`
5. Press `⌘+Z`

**Expected Result**:
- ✅ Each combination should display: "⌘+C - Copy", "⌘+V - Paste", etc.
- ✅ Display should disappear after 2 seconds of inactivity
- ✅ Format should be single line with action description

**Actual Result**: _[To be filled during testing]_

#### Test 1.3: Option Key Combinations  
**Objective**: Verify Option (⌥) combinations are displayed

**Test Steps**:
1. Press `⌥+A`
2. Press `⌥+Tab`
3. Press `⌥+Space`

**Expected Result**:
- ✅ Each combination should display properly
- ✅ Format: "⌥+A", "⌥+TAB", "⌥+SPACE"

**Actual Result**: _[To be filled during testing]_

#### Test 1.4: Control Key Combinations
**Objective**: Verify Control (⌃) combinations are displayed

**Test Steps**:
1. Press `⌃+A`
2. Press `⌃+C`
3. Press `⌃+D`

**Expected Result**:
- ✅ Each combination should display properly  
- ✅ Format: "⌃+A", "⌃+C", "⌃+D"

**Actual Result**: _[To be filled during testing]_

### 2. Shift Key Behavior Tests

#### Test 2.1: Shift + Regular Letters (Should be filtered)
**Objective**: Verify shift + regular letters are filtered out

**Test Steps**:
1. Press `⇧+A` (Shift+A)
2. Press `⇧+B` (Shift+B)
3. Press `⇧+1` (Shift+1)

**Expected Result**:
- ✅ No display should appear (these are just capitalization/symbols)
- ✅ Overlay should remain empty

**Actual Result**: _[To be filled during testing]_

#### Test 2.2: Shift + Special Keys (Should be allowed)
**Objective**: Verify shift + special keys are displayed

**Test Steps**:
1. Press `⇧+Tab`
2. Press `⇧+Space`  
3. Press `⇧+Return`
4. Press `⇧+Delete`
5. Press `⇧+Escape`

**Expected Result**:
- ✅ Each combination should display: "⇧+TAB", "⇧+SPACE", etc.
- ✅ These are meaningful shortcuts, not just capitalization

**Actual Result**: _[To be filled during testing]_

### 3. Multi-Modifier Combinations

#### Test 3.1: Command + Shift Combinations
**Objective**: Verify multi-modifier combinations work properly

**Test Steps**:
1. Press `⌘+⇧+Z` (Redo)
2. Press `⌘+⇧+S` (Save As)
3. Press `⌘+⇧+3` (Screenshot)
4. Press `⌘+⇧+4` (Screenshot Selection)

**Expected Result**:
- ✅ Display: "⌘+⇧+Z - Redo", "⌘+⇧+S - Save As", etc.
- ✅ Action descriptions should appear for known shortcuts

**Actual Result**: _[To be filled during testing]_

#### Test 3.2: Command + Option Combinations
**Objective**: Verify Command + Option combinations

**Test Steps**:
1. Press `⌘+⌥+D` (Show/Hide Dock)
2. Press `⌘+⌥+Esc` (Force Quit)

**Expected Result**:
- ✅ Display: "⌘+⌥+D - Show/Hide Dock", "⌘+⌥+ESC - Force Quit"

**Actual Result**: _[To be filled during testing]_

### 4. Display Format Tests

#### Test 4.1: Action Description Mapping
**Objective**: Verify common shortcuts show action descriptions

**Test Steps**:
Test each of these shortcuts and verify the exact display format:

| Shortcut | Expected Display |
|----------|------------------|
| ⌘+C | ⌘+C - Copy |
| ⌘+V | ⌘+V - Paste |
| ⌘+X | ⌘+X - Cut |
| ⌘+Z | ⌘+Z - Undo |
| ⌘+S | ⌘+S - Save |
| ⌘+A | ⌘+A - Select All |
| ⌘+F | ⌘+F - Find |
| ⌘+Q | ⌘+Q - Quit |
| ⌘+Space | ⌘+SPACE - Spotlight |
| ⌘+Tab | ⌘+TAB - Switch App |

**Expected Result**:
- ✅ Each shortcut displays action description
- ✅ Format is consistent: "Keys - Action"
- ✅ No newlines in display

**Actual Result**: _[To be filled during testing]_

#### Test 4.2: Unknown Combinations
**Objective**: Verify unknown combinations display without action

**Test Steps**:
1. Press `⌘+B` (no specific action mapped)
2. Press `⌥+K` (no specific action mapped)
3. Press `⌃+L` (no specific action mapped)

**Expected Result**:
- ✅ Display shows just the key combination: "⌘+B", "⌥+K", "⌃+L"
- ✅ No action description (empty)

**Actual Result**: _[To be filled during testing]_

### 5. Edge Cases and Special Keys

#### Test 5.1: Special Character Keys
**Objective**: Test special characters and symbols

**Test Steps**:
1. Press `⌘+,` (Preferences)
2. Press `⌘+.`
3. Press `⌘+/`
4. Press `⌘+[`
5. Press `⌘+]`

**Expected Result**:
- ✅ Special characters display properly
- ✅ `⌘+,` should show "⌘+, - Preferences"

**Actual Result**: _[To be filled during testing]_

#### Test 5.2: Function Keys
**Objective**: Test function key behavior

**Test Steps**:
1. Press `⌘+F1`
2. Press `⌘+F2`
3. Press `⌘+F12`

**Expected Result**:
- ✅ Function keys should display properly with command
- ✅ Format: "⌘+F1", "⌘+F2", etc.

**Actual Result**: _[To be filled during testing]_

### 6. Performance and Behavior Tests

#### Test 6.1: Rapid Key Presses
**Objective**: Test system behavior with rapid inputs

**Test Steps**:
1. Rapidly press `⌘+C`, `⌘+V`, `⌘+C`, `⌘+V` in quick succession
2. Hold `⌘` and press multiple letters quickly
3. Rapidly press various modifier combinations

**Expected Result**:
- ✅ Overlay updates smoothly without lag
- ✅ No crashes or system freezes
- ✅ Latest combination is displayed correctly

**Actual Result**: _[To be filled during testing]_

#### Test 6.2: Timer Behavior
**Objective**: Verify auto-hide timer works correctly

**Test Steps**:
1. Press `⌘+C` and wait exactly 2 seconds
2. Press `⌘+V` and wait 3 seconds
3. Press `⌘+S` and press another key before 2 seconds

**Expected Result**:
- ✅ Display clears after 2 seconds of inactivity
- ✅ New key presses reset the timer
- ✅ Timer behavior is consistent

**Actual Result**: _[To be filled during testing]_

#### Test 6.3: Modifier Hold Behavior
**Objective**: Test behavior when holding modifiers

**Test Steps**:
1. Hold `⌘` key down (no other keys)
2. Hold `⌥` key down (no other keys)
3. Hold `⌃` key down (no other keys)
4. Hold `⇧` key down (no other keys)

**Expected Result**:
- ✅ Should show "⌘...", "⌥...", "⌃..." for meaningful modifiers
- ✅ Should NOT show anything for `⇧` alone (not meaningful)

**Actual Result**: _[To be filled during testing]_

### 7. Regression Tests

#### Test 7.1: Basic Functionality Preserved
**Objective**: Ensure existing functionality still works

**Test Steps**:
1. Verify overlay window appears in bottom-right corner
2. Verify overlay is semi-transparent black
3. Verify overlay text is white and centered
4. Verify overlay can be moved by dragging
5. Verify overlay stays on top of other windows

**Expected Result**:
- ✅ All existing UI behavior preserved
- ✅ No visual regressions

**Actual Result**: _[To be filled during testing]_

#### Test 7.2: Application Lifecycle
**Objective**: Test application startup and shutdown

**Test Steps**:
1. Launch application
2. Grant accessibility permissions if prompted
3. Test several shortcuts
4. Quit with Ctrl+C in terminal

**Expected Result**:
- ✅ Clean startup with proper permission request
- ✅ Immediate responsiveness to shortcuts
- ✅ Clean shutdown without errors

**Actual Result**: _[To be filled during testing]_

## Quality Metrics

### Coverage Checklist
- [ ] Single letter filtering (blocks noise)
- [ ] Command key combinations (all major shortcuts)
- [ ] Option key combinations
- [ ] Control key combinations  
- [ ] Shift key filtering (only meaningful combinations)
- [ ] Multi-modifier combinations
- [ ] Action description mapping
- [ ] Special character handling
- [ ] Timer and auto-hide behavior
- [ ] Performance under rapid input
- [ ] UI regression testing

### Performance Criteria
- [ ] No noticeable lag in display updates
- [ ] Smooth operation under rapid key presses
- [ ] Memory usage remains stable
- [ ] CPU usage is minimal during idle

### User Experience Criteria
- [ ] Significantly reduced noise from single letters
- [ ] Clear, readable shortcut displays
- [ ] Helpful action descriptions for common shortcuts
- [ ] Intuitive behavior that matches user expectations

## Bug Report Template

If issues are found during testing:

**Bug ID**: [Unique identifier]
**Severity**: Critical/High/Medium/Low
**Test Scenario**: [Which test revealed the issue]
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]
**Actual Result**: [What actually happened]
**Environment**: macOS version, Swift version
**Additional Notes**: [Any other relevant information]

## Test Execution Notes

**Tester**: [Name]
**Date**: [Test execution date]
**Environment**: [macOS version, hardware details]
**Test Duration**: [How long testing took]
**Overall Assessment**: [Pass/Fail with summary]

**Critical Issues Found**: [List any blocking issues]
**Minor Issues Found**: [List any non-blocking issues]
**Recommendations**: [Suggestions for improvement]