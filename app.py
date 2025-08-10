import threading
import cv2 as cv
import numpy as np
import time
import pyttsx3
from tensorflow.keras.models import load_model
from flask import Flask, render_template, Response
import warnings
warnings.filterwarnings("ignore")


# Load model
model = load_model("emotions_model.h5")
print("\nModel loaded and running!")

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')

# Labels for emotions
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Function to run speech in background
def speak_emotion(emotion):
    def _speak():
        if emotion_labels == "Fear":
            engine.say(f"You look {emotion.lower()}ful")  # fearful
        elif emotion_labels == "Surprise":
            engine.say(f"You look {emotion.lower()}d")    # surprised
        else:
            engine.say(f"You look {emotion.lower()}")
        engine.runAndWait()
        
    threading.Thread(target=_speak, daemon=True).start()


# Load face cascade
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start camera
cap = cv.VideoCapture(0)

app = Flask(__name__)


def gen_frames():
    
    # detection frequency
    last_spoken_time = 0
    speak_interval = 7  #7 seconds
    detect_interval = 10  #frames between predictions
    last_spoken_emotion = None
    frame_counter = 0
    
    

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        #flip video output horizontally
        frame = cv.flip(frame, 1)
        
        # Convert to grayscale
        frame2gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(frame2gray, scaleFactor=1.2, minNeighbors=5)
        
        if len(faces) > 0:
            
            # use only the first face detected
            (x, y, w, h) = faces[0]  
        
            face = frame2gray[y:y+h, x:x+w]
            face_resized = cv.resize(face, (48, 48))
            face_normalized = face_resized / 255.0
            face_reshaped = np.reshape(face_normalized, (1, 48, 48, 1))

            # Prediction
            prediction = model.predict(face_reshaped, verbose=0)
            emotion_index = np.argmax(prediction)
            predicted_emotion = emotion_labels[emotion_index]
            confidence = np.max(prediction) * 100
            
            #print predicted values
            print("\nRaw Prediction", prediction)
            

            # Draw rectangle around face
            color = (0, 0, 255) if predicted_emotion == 'Happy' else (255, 0, 0)
            cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            label = f"{predicted_emotion} ({confidence:.1f}%)"
            cv.putText(frame, label, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            
            # Speak if detected another emotion and time interval crossed
            current_time = time.time()
            
            if (predicted_emotion != last_spoken_emotion) or (current_time - last_spoken_time > speak_interval):
                speak_emotion(predicted_emotion)
                last_spoken_emotion = predicted_emotion
                last_spoken_time = current_time
                
                
        # Encode frame to JPEG
        ret, buffer = cv.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
