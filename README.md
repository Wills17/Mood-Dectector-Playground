# EmotiSense – AI Emotion Detection

EmotiSense is a **real-time facial emotion detection app**  powered by TensorFlow, OpenCV, and Flask. Detect emotions from your webcam directly in the browser or run a local version with speech feedback.

---

## 🚀 Demo
Try it live here: [EmotiSense on Render](https://mood-dectector-playground.onrender.com)

---

## 🚀 Features

- Detects **7 emotions**: Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise.

- **Real-time webcam detection**

- **Two modes:**

  - 🟢 `app_r.py` → Lightweight TFLite model for deployment.
  - 🖥️ `app.py` → Local version with speech feedback (using `.h5`)

- **Mediapipe Mesh Demo** (`main.py`) → Rule-based emotion estimation using mathematical facial landmark calculations (no deep learning).

- **Web Interface** with modern UI (`home.html`, `detect.html`)

- **Secure & Private** → All inference happens locally in-browser.

## 📂 Project Structure

- **Models/**
  - `emotion_model.h5` → Keras model
  - `emotion_model.tflite` → TFLite model (for deployment)

- **static/**
  - `scripts.js`
  - `styles.css`

- **templates/**
  - `detect.html`
  - `home.html`

- `app.py` → Local version (uses `.h5` model, opens via localhost)  
- `app_r.py` → Render/live version (uses `.tflite` model)  
- `main.py` → Demo with Mediapipe face mesh & math-based mood detection  
- `model_train.ipynb`  
- `model_train.py`  
- `requirements.txt`  
- `render.yaml`

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

## ⚙️ How It Works

- **app.py** → Uses `.h5` TensorFlow/Keras model, runs locally (`python app.py`) and opens in the browser.  
- **app_r.py** → Optimized for deployment, runs on `.tflite` model for faster inference.  
- **main.py** → Alternative demo using Mediapipe face mesh + mathematical rules (no training data).  
  Displays **webcam + avatar mesh side by side**.

---

## ▶️ Running the App

### Local Version (.h5 model)
```bash
python app.py
```

---

### Live/Optimized Version (.tflite model)
```bash
python app_r.py
```
Runs using TensorFlow Lite for faster inference.

---

Then open in your browser:  
👉 `http://127.0.0.1:5000`

### Mediapipe Math-Based Demo
```bash
python main.py
```
Shows **camera feed + mesh overlay side by side** and calculates moods using geometry, not trained data.


## 📦 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Key dependencies:
- Flask  
- TensorFlow / TFLite  
- OpenCV  
- NumPy  
- Pillow  
- Gunicorn  

---
