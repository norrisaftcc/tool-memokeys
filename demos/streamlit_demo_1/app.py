import streamlit as st
import streamlit.components.v1 as components

# Quiz data
SHORTCUTS = [
    {
        "action": "Copy selected text",
        "answer": "ctrl+c",
        "description": "Copy"
    },
    {
        "action": "Paste copied text", 
        "answer": "ctrl+v",
        "description": "Paste"
    },
    {
        "action": "Cut selected text",
        "answer": "ctrl+x", 
        "description": "Cut"
    },
    {
        "action": "Undo the last action",
        "answer": "ctrl+z",
        "description": "Undo"
    },
    {
        "action": "Redo the last undone action",
        "answer": "ctrl+y",
        "description": "Redo"
    }
]

# JavaScript component for keyboard detection
def keyboard_detector():
    return components.html("""
        <div style="padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center;">
            <h3>Press the keyboard shortcut now!</h3>
            <p id="status">Listening for keyboard shortcut...</p>
            <div id="keys-pressed" style="font-size: 18px; font-weight: bold; margin-top: 10px;"></div>
        </div>
        
        <script>
            let pressedKeys = new Set();
            let keyCombo = '';
            
            function updateDisplay() {
                const keysArray = Array.from(pressedKeys).sort();
                document.getElementById('keys-pressed').textContent = 
                    keysArray.length > 0 ? keysArray.join(' + ') : '';
            }
            
            function normalizeKey(key) {
                const keyMap = {
                    'Control': 'Ctrl',
                    'Alt': 'Alt',
                    'Shift': 'Shift',
                    'Meta': 'Cmd'
                };
                return keyMap[key] || key.toUpperCase();
            }
            
            document.addEventListener('keydown', function(event) {
                event.preventDefault();
                
                if (event.ctrlKey) pressedKeys.add('Ctrl');
                if (event.altKey) pressedKeys.add('Alt');
                if (event.shiftKey) pressedKeys.add('Shift');
                if (event.metaKey) pressedKeys.add('Cmd');
                
                if (!['Control', 'Alt', 'Shift', 'Meta'].includes(event.key)) {
                    pressedKeys.add(normalizeKey(event.key));
                }
                
                updateDisplay();
                
                // Send the combination to Streamlit after a short delay
                if (pressedKeys.size >= 2) {
                    setTimeout(() => {
                        const combo = Array.from(pressedKeys).sort().join('+').toLowerCase();
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: combo
                        }, '*');
                    }, 100);
                }
            });
            
            document.addEventListener('keyup', function(event) {
                // Clear all keys on any key release to reset for next attempt
                pressedKeys.clear();
                updateDisplay();
                document.getElementById('status').textContent = 'Listening for keyboard shortcut...';
            });
            
            // Focus the document to capture key events
            document.addEventListener('DOMContentLoaded', function() {
                document.body.focus();
            });
        </script>
    """, height=150)

# Initialize session state
def init_session_state():
    if 'test_active' not in st.session_state:
        st.session_state.test_active = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'test_completed' not in st.session_state:
        st.session_state.test_completed = False
    if 'answers' not in st.session_state:
        st.session_state.answers = []

def start_test():
    st.session_state.test_active = True
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.test_completed = False
    st.session_state.answers = []

def restart_test():
    start_test()

def validate_answer(user_answer, correct_answer):
    # Handle None or non-string inputs
    if not user_answer:
        return False
    
    # Convert to string if needed and normalize
    user_str = str(user_answer) if user_answer is not None else ""
    user_clean = user_str.lower().strip().replace(" ", "").replace("+", "")
    correct_clean = correct_answer.lower().strip().replace(" ", "").replace("+", "")
    return user_clean == correct_clean

def next_question(user_answer):
    current = st.session_state.current_question
    correct_answer = SHORTCUTS[current]["answer"]
    is_correct = validate_answer(user_answer, correct_answer)
    
    # Store the answer
    st.session_state.answers.append({
        "action": SHORTCUTS[current]["action"],
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct
    })
    
    if is_correct:
        st.session_state.score += 1
    
    st.session_state.current_question += 1
    
    if st.session_state.current_question >= len(SHORTCUTS):
        st.session_state.test_completed = True
        st.session_state.test_active = False

def main():
    st.set_page_config(
        page_title="MemoKeys - Keyboard Shortcut Tester",
        page_icon="⌨️",
        layout="centered"
    )
    
    init_session_state()
    
    st.title("⌨️ MemoKeys")
    st.subheader("Test your keyboard shortcut knowledge")
    
    if not st.session_state.test_active and not st.session_state.test_completed:
        # Welcome screen
        st.write("Welcome to MemoKeys! Test your knowledge of essential keyboard shortcuts.")
        st.write("You'll be asked about 5 common shortcuts. Type your answers in the format 'Ctrl+C'.")
        
        if st.button("Start Test", type="primary", use_container_width=True):
            start_test()
            st.rerun()
    
    elif st.session_state.test_active:
        # Active test
        current = st.session_state.current_question
        total = len(SHORTCUTS)
        
        # Progress indicator
        progress = current / total
        st.progress(progress, text=f"Question {current + 1} of {total}")
        
        # Current question
        st.write(f"### {SHORTCUTS[current]['action']}")
        st.write("Press the keyboard shortcut to perform this action:")
        
        # Keyboard detector
        detected_shortcut = keyboard_detector()
        
        # Debug info
        if detected_shortcut:
            st.write(f"Detected: {detected_shortcut}")
            if st.button("Submit This Shortcut"):
                next_question(detected_shortcut)
                st.rerun()
        
        # Manual input as fallback
        with st.expander("Can't press keys? Type your answer here"):
            manual_answer = st.text_input(
                "Type the shortcut:",
                placeholder="Type here as fallback",
                key=f"manual_{current}"
            )
            if st.button("Submit Typed Answer", disabled=not manual_answer):
                next_question(manual_answer)
                st.rerun()
        
        # Show current score
        st.write(f"**Current Score:** {st.session_state.score}/{current}")
    
    elif st.session_state.test_completed:
        # Results screen
        st.success("🎉 Test Complete!")
        
        score = st.session_state.score
        total = len(SHORTCUTS)
        percentage = (score / total) * 100
        
        st.write(f"### Your Score: {score}/{total} ({percentage:.0f}%)")
        
        # Score interpretation
        if percentage >= 80:
            st.success("Excellent! You're a keyboard shortcut master! 🏆")
        elif percentage >= 60:
            st.info("Good job! You know your shortcuts well. 👍")
        else:
            st.warning("Keep practicing! Keyboard shortcuts will save you time. 💪")
        
        # Show detailed results
        with st.expander("Review Your Answers"):
            for i, answer in enumerate(st.session_state.answers):
                icon = "✅" if answer["is_correct"] else "❌"
                st.write(f"{icon} **{answer['action']}**")
                st.write(f"Your answer: `{answer['user_answer']}`")
                if not answer["is_correct"]:
                    st.write(f"Correct answer: `{answer['correct_answer']}`")
                st.write("---")
        
        if st.button("Take Test Again", type="primary", use_container_width=True):
            restart_test()
            st.rerun()

if __name__ == "__main__":
    main()