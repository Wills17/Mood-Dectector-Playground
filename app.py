import io
import base64
import time
import threading
import warnings
from PIL import Image
import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings("ignore")


# Load model
model = load_model("emotions_model.h5")
print("\nModel loaded and running!")

# Warm up model preventing first predict lag
warmup = model.predict(np.zeros((1, 48, 48, 1)), verbose=0)
print(warmup, "\n\nModel warmed up and ready for prediction!")

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')


# Labels for emotions
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# # Initialize TTS
# engine = pyttsx3.init()
# engine.setProperty('rate', 160)

# # Function to run speech in background
# def speak_emotion(emotion):
#     def _speak():
#         if emotion== "Fear":
#             engine.say(f"You look {emotion.lower()}ful")  # fearful
#         elif emotion == "Surprise":
#             engine.say(f"You look {emotion.lower()}d")    # surprised
#         else:
#             engine.say(f"You look {emotion.lower()}")
#         engine.runAndWait()
        
#     threading.Thread(target=_speak, daemon=True).start()


# Preprocess PIL image
def preprocess_pil_image(img: Image.Image) -> np.ndarray:
    """Convert PIL image to model's input method (gray, resized, normalized)."""

    img = img.convert("L") # grayscale
    img = img.resize((48, 48), Image.BILINEAR)
    img = np.asarray(img).astype("float32") / 255.0
    processed_img = np.expand_dims(img, axis=(0, -1))  # shape (1, H, W, 1)
    return processed_img


# Make prediction from PIL image
def predict_from_pil(img: Image.Image):
    
    x = preprocess_pil_image(img)
    preds = model.predict(x, verbose=0)[0]
    idx = int(np.argmax(preds))
    emotion = emotion_labels[idx]
    confidence = float(preds[idx]) * 100.0
    return emotion, confidence, preds.tolist()


@app.route("/predict_frame", methods=["POST"])
def predict_frame():
    """
    Accepts either:
     - multipart/form-data with a file field named 'frame' (bytes of JPEG/PNG)
     - JSON body with {"image": "data:image/jpeg;base64,...."}
    Returns JSON: { emotion, confidence, probs }
    """
    try:
        # 1) file upload via form
        if "frame" in request.files:
            file = request.files["frame"]
            img = Image.open(file.stream)
        else:
            data = None
            if request.is_json:
                data = request.get_json(silent=True)
            else:
                data = request.form.to_dict(flat=True)

            b64 = None
            if data:
                # handle JSON or form key "image"
                b64 = data.get("image") or data.get("frame") or data.get("data")
            if not b64:
                return jsonify({"error": "No image provided"}), 400

            # strip data URI prefix if present
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            img_bytes = base64.b64decode(b64)
            img = Image.open(io.BytesIO(img_bytes))

        emotion, confidence, probs = predict_from_pil(img)
        return jsonify({
            "emotion": emotion,
            "confidence": round(confidence, 2),
            "probs": probs
        })
    except Exception as e:
        app.logger.exception("predict_frame error")
        return jsonify({"error": str(e)}), 500


# home page
@app.route('/')
def home():
    return render_template('home.html')


# detect page
@app.route('/detect')
def detect():
    return render_template('detect.html')


# Health status check 
@app.route("/status")
def status():
    return jsonify({"status": "ok", "model": model, "timestamp": time.time()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    


# # Load face cascade

# face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

# # Start camera
# cap = cv.VideoCapture(0)

# def generate_frames():
    
#     # detection frequency
#     last_spoken_time = 0
#     speak_interval = 7  #7 seconds
#     detect_interval = 10  #frames between predictions
#     last_spoken_emotion = None
#     frame_count = 0
    
    
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         #flip video output horizontally
#         frame = cv.flip(frame, 1)
        
#         # Convert to grayscale
#         frame2gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

#         # Detect faces
#         faces = face_cascade.detectMultiScale(frame2gray, scaleFactor=1.2, minNeighbors=5, minSize=(48, 48))
        
#         if len(faces) > 0:
#             # Only keep the largest face
#             x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
            
#             # Preprocess detected face
#             face = frame2gray[y:y+h, x:x+w]
#             face_resized = cv.resize(face, (48, 48))
#             face_normalized = face_resized.astype("float32") / 255.0
#             face_reshaped = np.reshape(face_normalized, (1, 48, 48, 1))

#             if frame_count % detect_interval == 0:
#                 # Prediction
#                 prediction = model.predict(face_reshaped, verbose=0)
#                 emotion_index = int(np.argmax(prediction))
#                 predicted_emotion = emotion_labels[emotion_index]
#                 confidence = np.max(prediction) * 100
                
#                 #print predicted values
#                 print("\nDetections:", prediction)
#                 print("Prediction:", predicted_emotion)
            
#             # Draw rectangle around face
#             cv.rectangle(frame, (x, y), (x + w, y + h), (100, 200, 225), 2)

#             label = f"{predicted_emotion} ({confidence:.1f}%)"
#             cv.putText(frame, label, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (100, 200, 225), 2)
                
                
#             # Speak if detected another emotion and time interval crossed
#             current_time = time.time()
            
#             if (predicted_emotion != last_spoken_emotion) or (current_time - last_spoken_time > speak_interval):
#                 speak_emotion(predicted_emotion)
#                 last_spoken_emotion = predicted_emotion
#                 last_spoken_time = current_time
                
#         frame_count += 1
                
#         # Encode frame to JPEG
#         ret, buffer = cv.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# # video feed route
# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#      app.run(debug=True)
     

