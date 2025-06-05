import streamlit as st

# Quiz data
SHORTCUTS = [
    {
        "question": "What shortcut copies selected text?",
        "answer": "ctrl+c",
        "description": "Copy"
    },
    {
        "question": "What shortcut pastes copied text?", 
        "answer": "ctrl+v",
        "description": "Paste"
    },
    {
        "question": "What shortcut cuts selected text?",
        "answer": "ctrl+x", 
        "description": "Cut"
    },
    {
        "question": "What shortcut undoes the last action?",
        "answer": "ctrl+z",
        "description": "Undo"
    },
    {
        "question": "What shortcut redoes the last undone action?",
        "answer": "ctrl+y",
        "description": "Redo"
    }
]

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
    # Normalize input: lowercase, remove extra spaces
    user_clean = user_answer.lower().strip().replace(" ", "")
    correct_clean = correct_answer.lower().strip().replace(" ", "")
    return user_clean == correct_clean

def next_question(user_answer):
    current = st.session_state.current_question
    correct_answer = SHORTCUTS[current]["answer"]
    is_correct = validate_answer(user_answer, correct_answer)
    
    # Store the answer
    st.session_state.answers.append({
        "question": SHORTCUTS[current]["question"],
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
        st.write(f"### {SHORTCUTS[current]['question']}")
        
        # Answer input
        user_answer = st.text_input(
            "Your answer:",
            placeholder="e.g., Ctrl+C",
            key=f"answer_{current}"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col2:
            if st.button("Submit Answer", type="primary", disabled=not user_answer):
                next_question(user_answer)
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
                st.write(f"{icon} **{answer['question']}**")
                st.write(f"Your answer: `{answer['user_answer']}`")
                if not answer["is_correct"]:
                    st.write(f"Correct answer: `{answer['correct_answer']}`")
                st.write("---")
        
        if st.button("Take Test Again", type="primary", use_container_width=True):
            restart_test()
            st.rerun()

if __name__ == "__main__":
    main()