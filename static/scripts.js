// state variables 
let isDetecting = false;
let cameraEnabled = false;
let audioEnabled = false;
let detectionInterval;
let videoElement;

const emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
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
const toggleAudioBtn = document.getElementById('toggleAudio');
const emotionEmoji = document.getElementById('emotionEmoji');
const emotionName = document.getElementById('emotionName');
const emotionSpeech = document.getElementById('emotionSpeech');
const historyList = document.getElementById('historyList');
const cameraOffState = document.getElementById('cameraOffState');
const cameraOnState = document.getElementById('cameraOnState');
const faceOverlay = document.getElementById('faceOverlay');

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
    emotionEmoji.textContent = "😐";
    emotionName.textContent = "Neutral";
    historyList.innerHTML = '<div class="empty-history"><p>No detections yet</p></div>';

    // Clear all bars on reset
    document.querySelectorAll('.confidence-fill').forEach(bar => {
        bar.style.width = '0%';
    });
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

            cameraOnState.innerHTML = ''; // clear old
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

function updateUIWithPrediction(emotion, confidence) {
    emotionEmoji.textContent = emotionEmojis[emotion];
    emotionName.textContent = `${emotion} (${confidence}%)`;
    emotionSpeech.textContent = `🎤 Spoke: "You look ${emotion.toLowerCase()}"`;

    const historyItem = 
    `<div class="history-item latest">
        <span class="history-emoji">${emotionEmojis[emotion]}</span>
        <span class="history-label">${emotion}</span>
        <span class="latest-badge">Latest</span>
    </div>`;
    historyList.innerHTML = historyItem + historyList.innerHTML;

    // Limit to 7 items
    const historyItems = historyList.querySelectorAll('.history-item');
    if (historyItems.length > 5) {
        for (let i = 5; i < historyItems.length; i++) {
            historyItems[i].remove();
        }
    }

    updateEmotionCards(emotion);
    updateEmotionCards(emotion);
}

function updateEmotionCards(activeEmotion) {
    document.querySelectorAll('.emotion-card').forEach(card => {
        const fillBar = card.querySelector('.confidence-fill');

        if (card.dataset.emotion === activeEmotion && isDetecting) {
            card.classList.add('active');
            fillBar.style.width = '100%'; // full bar for detected emotion
        } else {
            card.classList.remove('active');
            fillBar.style.width = '0%'; // empty otherwise
        }
    });
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

// Initialize defaults
updateCameraState();
updateAudioState();
