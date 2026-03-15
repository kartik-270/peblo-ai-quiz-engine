document.addEventListener('DOMContentLoaded', () => {
    fetchSubjects();
    initDropZone();
});

let currentQuizzes = [];
let currentQuestionIndex = 0;
let score = 0;
let selectedOption = null;
let timerInterval = null;
let secondsElapsed = 0;
let currentDifficulty = 'medium';
let studentId = `S_${Math.floor(Math.random() * 1000)}`;

// API Endpoints
const API_BASE = window.location.origin;

async function fetchSubjects() {
    const container = document.getElementById('subjects-container');
    try {
        // We'll infer subjects from our hardcoded list for now or get distinct topics if we had an endpoint
        // Since we know the database has 'Math', 'English', 'Science' from previous checks
        const subjects = [
            { id: 'math', name: 'Math', icon: 'fas fa-calculator', color: '#6366f1' },
            { id: 'science', name: 'Science', icon: 'fas fa-flask', color: '#10b981' },
            { id: 'english', name: 'English', icon: 'fas fa-book', color: '#f472b6' }
        ];

        container.innerHTML = '';
        subjects.forEach(sub => {
            const card = document.createElement('div');
            card.className = 'subject-card glass';
            card.style.setProperty('--primary', sub.color);
            card.innerHTML = `
                <i class="${sub.icon}"></i>
                <h3>${sub.name}</h3>
                <p>Interactive adaptive quiz</p>
                <div class="difficulty-picker mt-2">
                    <button class="btn btn-outline btn-xs" onclick="startQuiz('${sub.name}', 'easy')">Easy</button>
                    <button class="btn btn-primary btn-xs" onclick="startQuiz('${sub.name}', 'medium')">Medium</button>
                    <button class="btn btn-accent btn-xs" onclick="startQuiz('${sub.name}', 'hard')">Hard</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching subjects:', error);
        container.innerHTML = '<p class="error">Failed to load subjects.</p>';
    }
}

let currentTopic = '';
let questionsSeen = new Set();
let totalTarget = 5;

async function startQuiz(topic, difficulty) {
    const player = document.getElementById('quiz-player');
    const selector = document.getElementById('quizzes');
    const hero = document.querySelector('.hero-section');

    currentTopic = topic;
    currentDifficulty = difficulty;
    currentQuestionIndex = 0;
    score = 0;
    questionsSeen.clear();

    // Hide UI elements
    hero.classList.add('hidden');
    selector.classList.add('hidden');
    player.classList.remove('hidden');

    await fetchNextAdaptiveQuestion();
    startTimer();
}

async function fetchNextAdaptiveQuestion() {
    const player = document.getElementById('quiz-player');
    const btnNext = document.getElementById('btn-next');
    
    // Show loading state if needed
    document.getElementById('q-text').innerText = "Loading next question...";

    try {
        const url = `${API_BASE}/quiz/?topic=${encodeURIComponent(currentTopic)}&difficulty=${currentDifficulty}`;
        const response = await fetch(url);
        const data = await response.json();

        // Find a question we haven't seen yet
        let nextQ = data.find(q => !questionsSeen.has(q.question_id));

        if (!nextQ) {
            // If no NEW questions at this difficulty, try to get ANY new question for this topic
            // or we might need to trigger more generation.
            // But since our backend auto-generates if empty, we mostly care about repeats.
            alert('Running out of unique questions for this level. Generating more or ending quiz...');
            showResults();
            return;
        }

        currentQuizzes[currentQuestionIndex] = nextQ;
        questionsSeen.add(nextQ.question_id);
        showQuestion();
    } catch (error) {
        console.error('Error fetching question:', error);
        alert('Failed to load next question.');
    }
}

function showQuestion() {
    const q = currentQuizzes[currentQuestionIndex];
    if (!q) return;

    const qText = document.getElementById('q-text');
    const qOptions = document.getElementById('q-options');
    const counter = document.getElementById('question-counter');
    const progress = document.getElementById('progress-bar');
    const btnNext = document.getElementById('btn-next');

    // Title
    document.getElementById('current-quiz-title').innerText = `${currentTopic} - ${q.difficulty.toUpperCase()}`;

    // Counter & Progress
    counter.innerText = `Question ${currentQuestionIndex + 1} of ${totalTarget}`;
    progress.style.width = `${((currentQuestionIndex + 1) / totalTarget) * 100}%`;

    // Question Text
    qText.innerText = q.question || "Unable to load question text.";

    // Options
    qOptions.innerHTML = '';
    selectedOption = null;
    btnNext.disabled = true;
    btnNext.innerHTML = 'Next Question <i class="fas fa-arrow-right"></i>';

    const options = q.options || [];
    if (options.length > 0) {
        options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.innerText = opt;
            btn.onclick = () => selectOption(btn, opt);
            qOptions.appendChild(btn);
        });
    } else {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'option-btn glass-input';
        input.placeholder = 'Type your answer...';
        input.oninput = (e) => {
            selectedOption = e.target.value;
            btnNext.disabled = !selectedOption;
        };
        qOptions.appendChild(input);
    }
}

async function nextQuestion() {
    const q = currentQuizzes[currentQuestionIndex];
    if (!q || !selectedOption) return;

    const btnNext = document.getElementById('btn-next');
    btnNext.disabled = true;
    btnNext.innerHTML = 'Submitting... <i class="fas fa-spinner fa-spin"></i>';

    try {
        const response = await fetch(`${API_BASE}/submit-answer/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                question_id: q.question_id,
                selected_answer: selectedOption
            })
        });

        if (!response.ok) throw new Error('Submission failed');
        const result = await response.json();
        
        if (result.correct) {
            score++;
            showFeedback(true);
        } else {
            showFeedback(false);
        }

        // Adaptive Feedback
        if (result.next_difficulty && result.next_difficulty !== currentDifficulty) {
            const up = result.next_difficulty === 'hard' || (result.next_difficulty === 'medium' && currentDifficulty === 'easy');
            showAdaptNotice(result.next_difficulty, up);
            currentDifficulty = result.next_difficulty;
        }

        currentQuestionIndex++;
        selectedOption = null; // Clear selection for next
        
        setTimeout(() => {
            if (currentQuestionIndex < totalTarget) {
                fetchNextAdaptiveQuestion();
            } else {
                showResults();
            }
        }, 1000);

    } catch (error) {
        console.error('Error in nextQuestion:', error);
        alert('Could not submit answer. Moving to next...');
        currentQuestionIndex++;
        setTimeout(() => {
            if (currentQuestionIndex < totalTarget) {
                fetchNextAdaptiveQuestion();
            } else {
                showResults();
            }
        }, 500);
    }
}

function showResults() {
    stopTimer();
    document.getElementById('quiz-player').classList.add('hidden');
    document.getElementById('results-screen').classList.remove('hidden');
    
    document.getElementById('final-score').innerText = score;
    document.querySelector('.total').innerText = `/${currentQuizzes.length}`;
    
    const percentage = (score / currentQuizzes.length) * 100;
    const msg = document.getElementById('result-message');
    if (percentage >= 80) msg.innerText = "Wow! You're a master of this topic!";
    else if (percentage >= 50) msg.innerText = "Good job! A little more practice and you'll be perfect.";
    else msg.innerText = "Keep studying! You'll get it next time.";
}

function restartQuiz() {
    document.getElementById('results-screen').classList.add('hidden');
    currentQuestionIndex = 0;
    score = 0;
    document.getElementById('quiz-player').classList.remove('hidden');
    showQuestion();
    startTimer();
}

function exitQuiz() {
    stopTimer();
    document.getElementById('quiz-player').classList.add('hidden');
    document.getElementById('results-screen').classList.add('hidden');
    document.querySelector('.hero-section').classList.remove('hidden');
    document.getElementById('quizzes').classList.remove('hidden');
}

function showFeedback(isCorrect) {
    const box = document.getElementById('question-box');
    const color = isCorrect ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)';
    box.style.backgroundColor = color;
    setTimeout(() => box.style.backgroundColor = 'transparent', 1000);
}

function showAdaptNotice(newDiff, isLevelUp) {
    const notice = document.createElement('div');
    notice.className = `adapt-notice ${isLevelUp ? 'up' : 'down'}`;
    notice.innerHTML = `<i class="fas ${isLevelUp ? 'fa-arrow-up' : 'fa-arrow-down'}"></i> ${isLevelUp ? 'Level Up!' : 'Difficulty Adjusted'} → ${newDiff.toUpperCase()}`;
    document.body.appendChild(notice);
    setTimeout(() => notice.remove(), 3000);
}

// Timer Logic
function startTimer() {
    secondsElapsed = 0;
    updateTimerText();
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        secondsElapsed++;
        updateTimerText();
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function updateTimerText() {
    const mins = Math.floor(secondsElapsed / 60);
    const secs = secondsElapsed % 60;
    document.getElementById('quiz-timer').innerHTML = `<i class="far fa-clock"></i> ${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Ingest Logic
function showIngest() {
    document.getElementById('ingest-modal').classList.remove('hidden');
}

function hideIngest() {
    document.getElementById('ingest-modal').classList.add('hidden');
}

function initDropZone() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const ingestForm = document.getElementById('ingest-form');

    dropZone.onclick = () => fileInput.click();

    dropZone.ondragover = (e) => {
        e.preventDefault();
        dropZone.classList.add('hover');
    };

    dropZone.ondragleave = () => dropZone.classList.remove('hover');

    dropZone.ondrop = (e) => {
        e.preventDefault();
        dropZone.classList.remove('hover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFileInfo();
        }
    };

    fileInput.onchange = updateFileInfo;

    ingestForm.onsubmit = async (e) => {
        e.preventDefault();
        const file = fileInput.files[0];
        if (!file) return alert('Please select a file');

        const formData = new FormData();
        formData.append('file', file);

        const btn = document.getElementById('btn-upload');
        const status = document.getElementById('upload-status');
        
        btn.disabled = true;
        btn.innerText = 'Uploading & Processing...';

        try {
            const response = await fetch(`${API_BASE}/ingest/pdf`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                status.innerHTML = '<span class="text-success">Success! Content ingested.</span>';
                setTimeout(() => {
                    hideIngest();
                    clearFile();
                    status.innerHTML = '';
                    btn.disabled = false;
                    btn.innerText = 'Process Content';
                }, 2000);
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            status.innerHTML = '<span class="text-error">Error processing file.</span>';
            btn.disabled = false;
            btn.innerText = 'Process Content';
        }
    };
}

function updateFileInfo() {
    const input = document.getElementById('file-input');
    const info = document.getElementById('file-info');
    const name = document.getElementById('filename');
    if (input.files.length) {
        name.innerText = input.files[0].name;
        info.classList.remove('hidden');
    }
}

function clearFile() {
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').classList.add('hidden');
}
