// ====== State Variables ======
let isDetecting = false;
let currentEmotion = 'Neutral';
let detectionHistory = [];
let cameraEnabled = false;
let audioEnabled = false;
let detectionInterval;

const emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise'];
const emotionEmojis = {
    'Happy': '😊',
    'Sad': '😢',
    'Angry': '😠',
    'Fear': '😨',
    'Surprise': '😲',
    'Neutral': '😐',
    'Disgust': '🤢'
};

// ====== DOM Elements ======
const startStopBtn = document.getElementById('startStopBtn');
const resetBtn = document.getElementById('resetBtn');
const toggleCameraBtn = document.getElementById('toggleCamera');
const toggleAudioBtn = document.getElementById('toggleAudio');
const emotionEmoji = document.getElementById('emotionEmoji');
const emotionName = document.getElementById('emotionName');
const emotionSpeech = document.getElementById('emotionSpeech');
const historyList = document.getElementById('historyList');
const cameraOffState = document.getElementById('cameraOffState');
const cameraOnState = document.getElementById('cameraOnState');
const faceOverlay = document.getElementById('faceOverlay');
const videoStream = document.getElementById('videoStream');


// Event Listening
// Start/Stop Detection
startStopBtn.addEventListener('click', () => {
    isDetecting = !isDetecting;
    updateDetectionState();
});

// Reset
resetBtn.addEventListener('click', () => {
    isDetecting = false;
    currentEmotion = 'Neutral';
    detectionHistory = [];
    updateDetectionState();
    updateCurrentEmotion();
    updateHistory();
});

// Toggle Camera
toggleCameraBtn.addEventListener('click', () => {
    cameraEnabled = !cameraEnabled;
    updateCameraState();
});

// Toggle Audio
toggleAudioBtn.addEventListener('click', () => {
    audioEnabled = !audioEnabled;
    updateAudioState();
});

// Functions 

function updateDetectionState() {
    if (isDetecting) {
        startStopBtn.classList.add('detecting');
        startStopBtn.querySelector('.play-icon').classList.add('hidden');
        startStopBtn.querySelector('.pause-icon').classList.remove('hidden');
        startStopBtn.querySelector('.btn-text').textContent = 'Stop';
        emotionSpeech.classList.remove('hidden');

        // Start emotion simulation
        detectionInterval = setInterval(() => {
            const newEmotion = emotions[Math.floor(Math.random() * emotions.length)];
            currentEmotion = newEmotion;
            detectionHistory.unshift(newEmotion);
            if (detectionHistory.length > 10) detectionHistory.pop();

            updateCurrentEmotion();
            updateHistory();
            updateEmotionCards();
        }, 3000);

    } else {
        startStopBtn.classList.remove('detecting');
        startStopBtn.querySelector('.play-icon').classList.remove('hidden');
        startStopBtn.querySelector('.pause-icon').classList.add('hidden');
        startStopBtn.querySelector('.btn-text').textContent = 'Start';
        emotionSpeech.classList.add('hidden');

        if (detectionInterval) {
            clearInterval(detectionInterval);
        }
    }

    updateCameraState();
}

function updateCurrentEmotion() {
    emotionEmoji.textContent = emotionEmojis[currentEmotion];
    emotionName.textContent = currentEmotion;
    emotionSpeech.innerHTML = `🎤 Speaking: "You look ${currentEmotion.toLowerCase()}"`;

    if (isDetecting) {
        emotionEmoji.classList.add('float');
    } else {
        emotionEmoji.classList.remove('float');
    }
}

function updateHistory() {
    if (detectionHistory.length === 0) {
        historyList.innerHTML = '<div class="empty-history"><p>No detections yet</p></div>';
    } else {
        historyList.innerHTML = detectionHistory.map((emotion, index) => `
            <div class="history-item ${index === 0 ? 'latest' : ''}">
                <span class="history-emoji">${emotionEmojis[emotion]}</span>
                <span class="history-label">${emotion}</span>
                ${index === 0 ? '<span class="latest-badge">Latest</span>' : ''}
            </div>
        `).join('');
    }
}

function updateEmotionCards() {
    document.querySelectorAll('.emotion-card').forEach(card => {
        if (card.dataset.emotion === currentEmotion && isDetecting) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
}

function updateCameraState() {
    const shouldShowCamera = cameraEnabled && isDetecting;

    if (shouldShowCamera) {
        cameraOffState.classList.add('hidden');
        cameraOnState.classList.remove('hidden');
        faceOverlay.classList.remove('hidden');

        // 🔹 Load Flask video feed
        if (videoStream.src !== "/video_feed") {
            videoStream.src = "/video_feed";
        }

    } else {
        cameraOffState.classList.remove('hidden');
        cameraOnState.classList.add('hidden');
        faceOverlay.classList.add('hidden');

        // 🔹 Stop feed when camera off
        videoStream.src = "";
    }

    // Update camera button styles
    if (cameraEnabled) {
        toggleCameraBtn.querySelector('.camera-on-icon').classList.remove('hidden');
        toggleCameraBtn.querySelector('.camera-off-icon').classList.add('hidden');
        toggleCameraBtn.classList.add('active');
    } else {
        toggleCameraBtn.querySelector('.camera-on-icon').classList.add('hidden');
        toggleCameraBtn.querySelector('.camera-off-icon').classList.remove('hidden');
        toggleCameraBtn.classList.remove('active');
    }
}

function updateAudioState() {
    if (audioEnabled) {
        toggleAudioBtn.querySelector('.audio-on-icon').classList.remove('hidden');
        toggleAudioBtn.querySelector('.audio-off-icon').classList.add('hidden');
        toggleAudioBtn.classList.add('active');
    } else {
        toggleAudioBtn.querySelector('.audio-on-icon').classList.add('hidden');
        toggleAudioBtn.querySelector('.audio-off-icon').classList.remove('hidden');
        toggleAudioBtn.classList.remove('active');
    }
}

// Initialize
updateCurrentEmotion();
updateHistory();
updateCameraState();
updateAudioState();
