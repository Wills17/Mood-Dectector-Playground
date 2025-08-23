// State Variables
let isDetecting = false;
let cameraEnabled = false;
let detectionInterval;
let videoElement;
let lastSpokenEmotion = null;
let lastPrediction = null;

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


// Elements
const startStopBtn = document.getElementById('startStopBtn');
const resetBtn = document.getElementById('resetBtn');
const toggleCameraBtn = document.getElementById('toggleCamera');
const emotionEmoji = document.getElementById('emotionEmoji');
const emotionName = document.getElementById('emotionName');
const emotionSpeech = document.getElementById('emotionSpeech');
const historyList = document.getElementById('historyList');
const cameraOffState = document.getElementById('cameraOffState');
const cameraOnState = document.getElementById('cameraOnState');
const faceOverlay = document.getElementById('faceOverlay');


// define prediction interval for tweaking later.
const PREDICTION_INTERVAL = 2000; // ms



// Event Listeners
startStopBtn.addEventListener('click', () => {
    isDetecting = !isDetecting;
    updateDetectionState();
});

resetBtn.addEventListener('click', () => {
    stopDetection();
    isDetecting = false;
    updateDetectionState();
    emotionEmoji.textContent = "😐";
    emotionName.textContent = "Neutral";
    historyList.innerHTML = '<div class="empty-history"><p>No detections yet</p></div>';
    lastSpokenEmotion = null;
    lastPrediction = null;
});

toggleCameraBtn.addEventListener('click', () => {
    cameraEnabled = !cameraEnabled;
    updateCameraState();
});



// State Handlers
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


// Camera + Detection
function startCameraAndDetection() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement = document.createElement('video');
            videoElement.setAttribute('autoplay', true);
            videoElement.setAttribute('playsinline', true);
            videoElement.srcObject = stream;

            cameraOnState.innerHTML = ''; // clear old
            cameraOnState.appendChild(videoElement);

            detectionInterval = setInterval(captureFrame, PREDICTION_INTERVAL);
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


// UI Updates
function updateUIWithPrediction(emotion, confidence) {
    emotionEmoji.textContent = emotionEmojis[emotion];
    emotionName.textContent = `${emotion} (${confidence}%)`;

    // Speak only if emotion changed
    if (emotion !== lastSpokenEmotion) {
        let speechText;
        if (emotion === "Fear") {
            speechText = `You look fearful`;
        } else if (emotion === "Surprise") {
            speechText = `You look surprised`;
        } else {
            speechText = `You look ${emotion.toLowerCase()}`;
        }
        emotionSpeech.textContent = `🎤 ${speechText}`;
        const utterance = new SpeechSynthesisUtterance(speechText);
        utterance.rate = 1;
        utterance.pitch = 1;
        speechSynthesis.speak(utterance);

        lastSpokenEmotion = emotion;
    }

    // Update recent predictions (max 7, only if different from last one)
    if (emotion !== lastPrediction) {
        const historyItem = `<div class="history-item latest">
            <span class="history-emoji">${emotionEmojis[emotion]}</span>
            <span class="history-label">${emotion}</span>
            <span class="latest-badge">Latest</span>
        </div>`;

        const currentHistory = historyList.innerHTML;
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = historyItem + currentHistory;

        const items = tempDiv.querySelectorAll('.history-item');
        const limitedHistory = Array.from(items).slice(0, 7).map(item => item.outerHTML).join('');
        historyList.innerHTML = limitedHistory;

        lastPrediction = emotion;
    }

    // Update emotion cards with confidence
    updateEmotionCards(emotion, confidence);
}

function updateEmotionCards(activeEmotion, confidence) {
    document.querySelectorAll('.emotion-card').forEach(card => {
        const bar = card.querySelector('.confidence-fill');
        const valueLabel = card.querySelector('.confidence-value');

        if (card.dataset.emotion === activeEmotion && isDetecting) {
            card.classList.add('active');
            if (bar) bar.style.width = `${confidence}%`;
            if (valueLabel) valueLabel.textContent = `${confidence}%`;
        } else {
            card.classList.remove('active');
            if (bar) bar.style.width = `1%`;
            if (valueLabel) valueLabel.textContent = `1%`;
        }
    });
}


// Initialise Defaults
updateCameraState();
