class MemoKeys {
    constructor() {
        this.platform = this.detectPlatform();
        this.shortcuts = [];
        this.currentQuestionIndex = 0;
        this.score = 0;
        this.results = [];
        this.pressedKeys = new Set();
        this.isListening = false;
        this.selectedShortcutSet = null;
        this.availableShortcutSets = [];
        
        this.initializeElements();
        this.setupEventListeners();
        this.updatePlatformDisplay();
        this.loadShortcutSets();
    }

    detectPlatform() {
        const userAgent = navigator.userAgent;
        if (userAgent.includes('Mac')) return 'mac';
        if (userAgent.includes('Win')) return 'windows';
        return 'windows'; // Default to Windows
    }

    initializeElements() {
        // Screens
        this.welcomeScreen = document.getElementById('welcome-screen');
        this.testScreen = document.getElementById('test-screen');
        this.resultsScreen = document.getElementById('results-screen');
        
        // Controls
        this.themeToggle = document.getElementById('theme-toggle');
        this.platformSelect = document.getElementById('platform-select');
        this.startTestBtn = document.getElementById('start-test');
        this.skipBtn = document.getElementById('skip-btn');
        this.retryBtn = document.getElementById('retry-btn');
        
        // Test elements
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.actionPrompt = document.getElementById('action-prompt');
        this.keyDisplay = document.getElementById('key-display');
        this.feedback = document.getElementById('feedback');
        this.currentScore = document.getElementById('current-score');
        this.totalQuestions = document.getElementById('total-questions');
        
        // Results elements
        this.finalScore = document.getElementById('final-score');
        this.finalTotal = document.getElementById('final-total');
        this.percentage = document.getElementById('percentage');
        this.performanceMessage = document.getElementById('performance-message');
        this.resultsDetails = document.getElementById('results-details');
        
        // Platform display
        this.detectedPlatform = document.getElementById('detected-platform');
        
        // Shortcut set selection
        this.shortcutSetsContainer = document.getElementById('shortcut-sets-container');
        
        // Error message elements
        this.errorMessage = document.getElementById('error-message');
        this.errorText = this.errorMessage.querySelector('.error-text');
        this.errorClose = this.errorMessage.querySelector('.error-close');
    }

    setupEventListeners() {
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Platform selection
        this.platformSelect.addEventListener('change', (e) => {
            if (e.target.value === 'auto') {
                this.platform = this.detectPlatform();
            } else {
                this.platform = e.target.value;
            }
            this.updatePlatformDisplay();
        });
        
        // Navigation buttons
        this.startTestBtn.addEventListener('click', () => this.startTest());
        this.skipBtn.addEventListener('click', () => this.skipQuestion());
        this.retryBtn.addEventListener('click', () => this.resetTest());
        
        // Keyboard events
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
        
        // Error message close
        this.errorClose.addEventListener('click', () => this.hideError());
        
        // Prevent default for common shortcuts during test
        document.addEventListener('keydown', (e) => {
            if (this.isListening) {
                if (e.ctrlKey || e.metaKey || e.altKey) {
                    e.preventDefault();
                }
            }
        });
    }

    toggleTheme() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        this.themeToggle.textContent = isDark ? '☀️' : '🌙';
        
        // Save theme preference
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    updatePlatformDisplay() {
        this.detectedPlatform.textContent = this.platform === 'mac' ? 'macOS' : 'Windows';
        this.platformSelect.value = this.platform;
    }
    
    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.remove('hidden');
        // Auto-hide error after 10 seconds
        setTimeout(() => this.hideError(), 10000);
    }
    
    hideError() {
        this.errorMessage.classList.add('hidden');
    }
    
    async loadShortcutSets() {
        try {
            const response = await fetch('/api/shortcut-sets');
            if (!response.ok) {
                throw new Error(`Failed to load shortcut sets: ${response.status} ${response.statusText}`);
            }
            
            this.availableShortcutSets = await response.json();
            this.displayShortcutSets();
        } catch (error) {
            console.error('Error loading shortcut sets:', error);
            this.showError('Failed to load shortcut sets. Please check your connection and refresh the page.');
            this.shortcutSetsContainer.innerHTML = '<div class="error-state">Unable to load shortcut sets. Please try refreshing the page.</div>';
        }
    }
    
    displayShortcutSets() {
        this.shortcutSetsContainer.innerHTML = '';
        
        const groupedSets = this.availableShortcutSets.reduce((acc, set) => {
            if (!acc[set.category]) acc[set.category] = [];
            acc[set.category].push(set);
            return acc;
        }, {});
        
        Object.entries(groupedSets).forEach(([category, sets]) => {
            sets.forEach(set => {
                const card = document.createElement('div');
                card.className = 'shortcut-set-card';
                card.dataset.setId = set.id;
                
                card.innerHTML = `
                    <h4>${set.name}</h4>
                    <div class="category">${category}</div>
                    ${set.description ? `<div class="description">${set.description}</div>` : ''}
                `;
                
                card.addEventListener('click', () => this.selectShortcutSet(set));
                this.shortcutSetsContainer.appendChild(card);
            });
        });
    }
    
    selectShortcutSet(set) {
        // Remove previous selection
        document.querySelectorAll('.shortcut-set-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Mark new selection
        const selectedCard = document.querySelector(`[data-set-id="${set.id}"]`);
        selectedCard.classList.add('selected');
        
        this.selectedShortcutSet = set;
        this.startTestBtn.disabled = false;
        this.startTestBtn.textContent = `Start Test: ${set.name}`;
    }

    async loadShortcuts() {
        if (!this.selectedShortcutSet) {
            this.showError('Please select a shortcut set first');
            return false;
        }
        
        try {
            const response = await fetch(`/api/shortcuts/${this.selectedShortcutSet.id}/${this.platform}`);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to load shortcuts: ${response.status} ${response.statusText}. ${errorText}`);
            }
            
            const data = await response.json();
            this.shortcuts = data.shortcuts.slice(0, 5); // Limit to 5 for MVP
            return true;
        } catch (error) {
            console.error('Error loading shortcuts:', error);
            this.showError('Failed to load shortcuts. Please check your connection and try again.');
            return false;
        }
    }

    async startTest() {
        // Clear any existing errors
        this.hideError();
        
        const loaded = await this.loadShortcuts();
        if (!loaded) return;
        
        // Validate we have shortcuts to test
        if (!this.shortcuts || this.shortcuts.length === 0) {
            this.showError('No shortcuts available for this set. Please select a different set.');
            return;
        }
        
        this.currentQuestionIndex = 0;
        this.score = 0;
        this.results = [];
        
        this.showScreen('test');
        this.updateProgress();
        this.showQuestion();
    }

    showQuestion() {
        if (this.currentQuestionIndex >= this.shortcuts.length) {
            this.showResults();
            return;
        }
        
        const shortcut = this.shortcuts[this.currentQuestionIndex];
        this.actionPrompt.textContent = shortcut.action;
        this.keyDisplay.textContent = 'Press the shortcut...';
        this.keyDisplay.className = 'key-display listening';
        this.feedback.className = 'feedback';
        this.feedback.textContent = '';
        
        this.isListening = true;
        this.pressedKeys.clear();
        
        this.updateScore();
    }

    handleKeyDown(e) {
        if (!this.isListening) return;
        
        // Build the key combination
        const keys = [];
        
        if (e.ctrlKey) keys.push('Ctrl');
        if (e.metaKey) keys.push('Cmd');
        if (e.altKey) keys.push('Alt');
        if (e.shiftKey) keys.push('Shift');
        
        // Add the main key (if it's not a modifier)
        if (!['Control', 'Meta', 'Alt', 'Shift'].includes(e.key)) {
            keys.push(e.key.toUpperCase());
        }
        
        if (keys.length >= 2) { // At least modifier + key
            const combination = keys.join('+');
            this.keyDisplay.textContent = combination;
            
            // Check after a short delay to allow for complete key combination
            setTimeout(() => this.checkAnswer(combination), 100);
        }
    }

    handleKeyUp(e) {
        // Reset display when keys are released
        if (this.isListening && this.keyDisplay.textContent !== 'Press the shortcut...') {
            // Only reset if no keys are currently pressed
            setTimeout(() => {
                if (!e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey) {
                    this.pressedKeys.clear();
                }
            }, 50);
        }
    }

    checkAnswer(userInput) {
        if (!this.isListening) return;
        
        const currentShortcut = this.shortcuts[this.currentQuestionIndex];
        const correctAnswer = this.normalizeShortcut(currentShortcut.keys);
        const userAnswer = this.normalizeShortcut(userInput);
        
        const isCorrect = userAnswer === correctAnswer;
        
        // Stop listening
        this.isListening = false;
        
        // Show feedback
        this.showFeedback(isCorrect, currentShortcut.keys);
        
        // Record result
        this.results.push({
            action: currentShortcut.action,
            correctKeys: currentShortcut.keys,
            userKeys: userInput,
            correct: isCorrect
        });
        
        if (isCorrect) {
            this.score++;
        }
        
        // Move to next question after delay
        setTimeout(() => {
            this.currentQuestionIndex++;
            this.updateProgress();
            this.showQuestion();
        }, 2000);
    }

    normalizeShortcut(shortcut) {
        return shortcut
            .toLowerCase()
            .replace(/\s+/g, '')
            .replace(/cmd/g, 'ctrl') // Treat Cmd and Ctrl as equivalent for comparison
            .split('+')
            .sort()
            .join('+');
    }

    showFeedback(isCorrect, correctAnswer) {
        this.keyDisplay.className = `key-display ${isCorrect ? 'correct' : 'incorrect'}`;
        
        if (isCorrect) {
            this.feedback.textContent = '✅ Correct!';
            this.feedback.className = 'feedback correct show';
        } else {
            this.feedback.textContent = `❌ Correct answer: ${correctAnswer}`;
            this.feedback.className = 'feedback incorrect show';
        }
    }

    skipQuestion() {
        if (!this.isListening) return;
        
        const currentShortcut = this.shortcuts[this.currentQuestionIndex];
        
        // Record as incorrect
        this.results.push({
            action: currentShortcut.action,
            correctKeys: currentShortcut.keys,
            userKeys: 'Skipped',
            correct: false
        });
        
        this.isListening = false;
        this.showFeedback(false, currentShortcut.keys);
        
        setTimeout(() => {
            this.currentQuestionIndex++;
            this.updateProgress();
            this.showQuestion();
        }, 2000);
    }

    updateProgress() {
        const progress = (this.currentQuestionIndex / this.shortcuts.length) * 100;
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = `Question ${this.currentQuestionIndex + 1} of ${this.shortcuts.length}`;
    }

    updateScore() {
        this.currentScore.textContent = this.score;
        this.totalQuestions.textContent = this.shortcuts.length;
    }

    showResults() {
        const percentage = Math.round((this.score / this.shortcuts.length) * 100);
        
        this.finalScore.textContent = this.score;
        this.finalTotal.textContent = this.shortcuts.length;
        this.percentage.textContent = `${percentage}%`;
        
        // Performance message
        let message = '';
        if (percentage >= 90) {
            message = '🏆 Outstanding! You\'re a keyboard shortcut master!';
        } else if (percentage >= 70) {
            message = '🎯 Great job! You know your shortcuts well.';
        } else if (percentage >= 50) {
            message = '👍 Good effort! Keep practicing to improve.';
        } else {
            message = '💪 Keep learning! Shortcuts will save you time.';
        }
        this.performanceMessage.textContent = message;
        
        // Show detailed results
        this.populateResults();
        
        this.showScreen('results');
    }

    populateResults() {
        this.resultsDetails.innerHTML = '';
        
        this.results.forEach(result => {
            const item = document.createElement('div');
            item.className = `result-item ${result.correct ? 'correct' : 'incorrect'}`;
            
            item.innerHTML = `
                <div>
                    <div class="result-action">${result.action}</div>
                    <div class="result-shortcut">Correct: ${result.correctKeys}</div>
                    ${!result.correct ? `<div class="result-shortcut">Your answer: ${result.userKeys}</div>` : ''}
                </div>
                <div class="result-status ${result.correct ? 'correct' : 'incorrect'}">
                    ${result.correct ? '✅' : '❌'}
                </div>
            `;
            
            this.resultsDetails.appendChild(item);
        });
    }

    resetTest() {
        this.showScreen('welcome');
        this.isListening = false;
        this.pressedKeys.clear();
    }

    showScreen(screenName) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Show target screen
        const targetScreen = document.getElementById(`${screenName}-screen`);
        if (targetScreen) {
            targetScreen.classList.add('active');
        }
    }

    // Initialize theme on load
    initializeTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.body.classList.remove('dark-mode');
            this.themeToggle.textContent = '🌙';
        } else {
            document.body.classList.add('dark-mode');
            this.themeToggle.textContent = '☀️';
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new MemoKeys();
    app.initializeTheme();
});