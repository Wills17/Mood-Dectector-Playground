// State Variables
let isDetecting = false;
let cameraEnabled = false;
let audioEnabled = false;
let detectionInterval;
let videoElement;

// Emotions and mapping
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise'];
const emotionEmojis = {
    'Happy': '😊',
    'Sad': '😢',
    'Angry': '😠',
    'Fear': '😨',
    'Surprise': '😲',
    'Neutral': '😐',
    'Disgust': '🤢'
};

// Emotion detection counts
let emotionCounts = {
    Happy: 0,
    Neutral: 0,
    Surprise: 0,
    Sad: 0,
    Angry: 0,
    Fear: 0,
    Disgust: 0
};


// DOM Elements
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


// Event Listeners

// Start/Stop Detection
startStopBtn.addEventListener('click', () => {
    isDetecting = !isDetecting;
    updateDetectionState();
});

// Reset
resetBtn.addEventListener('click', () => {
    stopDetection();
    isDetecting = false;
    updateDetectionState();

    emotionEmoji.textContent = "🤔";
    emotionName.textContent = "Unknown";
    historyList.innerHTML = '<div class="empty-history"><p>No detections yet</p></div>';

    for (let key in emotionCounts) {
        emotionCounts[key] = 0;
        const el = document.querySelector(`.emotion-card[data-emotion="${key}"] .confidence-value`);
        if (el) el.textContent = "0";
    }
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



// Core Functions

function updateDetectionState() {
    if (isDetecting) {
        startStopBtn.classList.add('detecting');
        startStopBtn.querySelector('.play-icon').classList.add('hidden');
        startStopBtn.querySelector('.pause-icon').classList.remove('hidden');
        startStopBtn.querySelector('.btn-text').textContent = 'Stop';
        emotionSpeech.classList.remove('hidden');

        if (cameraEnabled) {
            startCameraAndDetection();
        }
    } else {
        startStopBtn.classList.remove('detecting');
        startStopBtn.querySelector('.play-icon').classList.remove('hidden');
        startStopBtn.querySelector('.pause-icon').classList.add('hidden');
        startStopBtn.querySelector('.btn-text').textContent = 'Start';
        emotionSpeech.classList.add('hidden');
        stopDetection();
    }
}

function startCameraAndDetection() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement = document.createElement('video');
            videoElement.setAttribute('autoplay', true);
            videoElement.setAttribute('playsinline', true);
            videoElement.srcObject = stream;

            cameraOnState.innerHTML = ''; // Clear old feed
            cameraOnState.appendChild(videoElement);

            detectionInterval = setInterval(captureFrame, 1000);
        })
        .catch(err => console.error("Camera access error:", err));
}

function stopDetection() {
    clearInterval(detectionInterval);
    if (videoElement && videoElement.srcObject) {
        videoElement.srcObject.getTracks().forEach(track => track.stop());
    }
}

function captureFrame() {
    if (!videoElement || videoElement.videoWidth === 0) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg');

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.emotion) {
            updateUIWithPrediction(data.emotion, data.confidence);
        }
    })
    .catch(err => console.error("Prediction error:", err));
}


// Emotion Count + UI Update
function updateEmotionCount(emotion) {
    if (emotionCounts.hasOwnProperty(emotion)) {
        emotionCounts[emotion]++;

        // Update count display
        const element = document.querySelector(
            `.emotion-card[data-emotion="${emotion}"] .confidence-value`
        );
        if (element) {
            element.textContent = emotionCounts[emotion];
        }
    }
}

function updateUIWithPrediction(emotion, confidence) {
    emotionEmoji.textContent = emotionEmojis[emotion];
    emotionName.textContent = emotion;
    emotionSpeech.textContent = `🎤 Speaking: "You look ${emotion.toLowerCase()}"`;

    // Update history
    const historyItem = `<div class="history-item latest">
        <span class="history-emoji">${emotionEmojis[emotion]}</span>
        <span class="history-label">${emotion}</span>
        <span class="latest-badge">Latest</span>
    </div>`;
    historyList.innerHTML = historyItem + historyList.innerHTML;

    updateEmotionCount(emotion);

    // Highlight active card
    updateEmotionCards(emotion);
}

function updateEmotionCards(activeEmotion) {
    document.querySelectorAll('.emotion-card').forEach(card => {
        if (card.dataset.emotion === activeEmotion && isDetecting) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
}


// Camera & Audio UI
function updateCameraState() {
    const shouldShowCamera = cameraEnabled && isDetecting;

    if (shouldShowCamera) {
        cameraOffState.classList.add('hidden');
        cameraOnState.classList.remove('hidden');
        faceOverlay.classList.remove('hidden');
        startCameraAndDetection();
    } else {
        cameraOffState.classList.remove('hidden');
        cameraOnState.classList.add('hidden');
        faceOverlay.classList.add('hidden');
        stopDetection();
    }

    // Button icon states
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


// Initialise states
updateCameraState();
updateAudioState();
