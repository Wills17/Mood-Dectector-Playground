# 😃 Mood Detector Playground

Real-time **facial emotion detection** powered by **TensorFlow, OpenCV, and Flask**. Detect emotions from your webcam directly in the browser or run a local version with **speech feedback**. Includes two versions: a **live TFLite deployment** and a **local .h5-based demo**.

---

## 🚀 Features

* Detects **7 emotions**: Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise
* **Real-time webcam detection**
* **Two modes**:

  * 🟢 `app_r.py` → Lightweight TFLite model for deployment
  * 🖥️ `app.py` → Local version with speech feedback (using `.h5`)
* **Mediapipe Mesh Demo (`main.py`)** → Rule-based emotion estimation using mathematical facial landmark calculations (no deep learning)
* **Web Interface** with modern UI (`home.html`, `detect.html`)
* **Secure & Private** → All inference happens locally in-browser

---

## 🗂️ Project Structure

```
MOOD-DETECTOR-PLAYGROUND/
│
├── Models/
│   ├── emotion_model.h5          # Keras model (local version)
│   └── emotion_model.tflite      # TFLite model (deployment)
│
├── static/
│   ├── images/
│   │   └── hero-emotion-ai.jpg
│   ├── scripts.js
│   └── styles.css
│
├── templates/
│   ├── home.html
│   └── detect.html
│
├── app.py                        # Local version (.h5, with TTS)
├── app_r.py                      # Deployment version (TFLite)
├── main.py                       # Mediapipe math-based demo
├── model_train.py                 # Model training script
├── model_train.ipynb              # Training notebook with results
├── requirements.txt
└── render.yaml (optional)
```

---

## 📊 Model Training

The CNN model was trained using the **Face Expression Recognition Dataset** (7 emotion classes).

### 🔹 Dataset

* Train/Test split: 80/20
* Image preprocessing:

  * Grayscale conversion
  * Resized to **48×48**
  * Normalized pixel values (0–1)

### 🔹 Model Architecture

* **Conv2D (64) → BatchNorm → MaxPool → Dropout (0.25)**
* **Conv2D (128) → BatchNorm → MaxPool → Dropout (0.25)**
* **Conv2D (256) → BatchNorm → MaxPool → Dropout (0.25)**
* **Flatten → Dense(512, ReLU) → Dropout (0.5)**
* **Dense(7, Softmax)**

### 🔹 Training

* Optimizer: **Adam (lr=0.001)**
* Loss: **Categorical Crossentropy (with label smoothing)**
* Data Augmentation: rotation (10°), zoom (10%), horizontal flips, shifts.
* Callbacks:

  * `EarlyStopping` (patience=5)
  * `ReduceLROnPlateau`
  * `ModelCheckpoint` (best weights only)

### 🔹 Results

* **Validation Accuracy**: \~56%
* **Confusion Matrix**: Strong on *Happy* & *Surprise*, weaker on *Disgust* & *Fear*
* Predictions plotted against ground truth in notebook

### 🔹 Outputs

* Final model saved as **`emotions_model3.h5`**
* Converted later into **`emotion_model.tflite`** for deployment

---

## ▶️ Running the App

### 1. Local version (`app.py`)

Runs the `.h5` model with **text-to-speech feedback**.

```bash
pip install -r requirements.txt
python app.py
```

Open in browser: `http://127.0.0.1:5000/`

### 2. Deployment version (`app_r.py`)

Runs the lightweight **TFLite model** (for Render/production).

```bash
pip install -r requirements.txt
python app_r.py
```

---

## 🧪 Mediapipe Demo (`main.py`)

This is an **alternative experiment** that doesn’t rely on CNN training. Instead, it uses:

* **FaceMesh landmarks** from Mediapipe
* **Mathematical ratios** of lip, eye, and iris distances
* Rule-based classification of moods (Happy, Sad, Angry, Surprised, Neutral, Fearful, Disgusted)
* Displays **webcam + avatar mesh side by side**

This version demonstrates how emotions can be inferred using **geometric features** instead of deep learning.

---

## 📦 Requirements

```
Flask
tensorflow
numpy
opencv-python-headless
Pillow
gunicorn
```
