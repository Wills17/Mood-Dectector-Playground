# import libraries
import threading
import cv2 as cv
import numpy as np
import base64
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, jsonify
import warnings
warnings.filterwarnings("ignore")



# Load model
model = load_model("emotions_model.h5")
print("\nModel loaded and running!")

model.predict(np.zeros((1, 48, 48, 1)), verbose=0)
print("Model warmup complete!")


# Initialize Flask
app = Flask(__name__, static_folder='static', template_folder='templates')

# Labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']


# Use face cascade
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

# home page
@app.route('/')
def home():
    return render_template('home.html')

# detect page
@app.route('/detect')
def detect():
    return render_template('detect.html')

# predict route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get image continously from request
        data = request.json['image']
        image_data = base64.b64decode(data.split(',')[1])
        np_array = np.frombuffer(image_data, np.uint8)
        frame = cv.imdecode(np_array, cv.IMREAD_COLOR)

        # Convert to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detect face
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(48, 48))
        
        if len(faces) == 0:
            # If no face, no predictions gotten
            _, buffer = cv.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return jsonify({"emotion": None, "confidence": 0, "frame": f"data:image/jpeg;base64,{frame_base64}"})


        # Use largest face
        x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
        face = gray[y:y+h, x:x+w]
        face_resized = cv.resize(face, (48, 48))
        face_normalized = face_resized.astype("float32") / 255.0
        face_reshaped = np.reshape(face_normalized, (1, 48, 48, 1))

        # Prediction
        prediction = model.predict(face_reshaped, verbose=0)
        emotion_index = int(np.argmax(prediction))
        predicted_emotion = emotion_labels[emotion_index]
        confidence = float(np.max(prediction) * 100)
        
        # Encode frame
        _, buffer = cv.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            "emotion": predicted_emotion,
            "confidence": round(confidence, 1),
            "frame": f"data:image/jpeg;base64,{frame_base64}"
            })

    except Exception as e:
        return jsonify({"error": str(e)})



# run app
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

