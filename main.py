# Facial and mood dectection using OpenCV and mediapipe

#Import necessary libraries
import cv2 as cv
import pyttsx3 as tts
import mediapipe as mp
import numpy as np
import time
import threading



# set up mediapipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,                    # detect up to 5 faces # detect one for now
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    refine_landmarks=True)

# set up mediapipe drawing utils
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
lips_connections = mp_face_mesh.FACEMESH_LIPS
LEFT_IRIS = [468, 469, 470, 471]
RIGHT_IRIS = [473, 474, 475, 476]



# Set up text-to-speech engine
engine = tts.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)



# Labels for emotions
mood_styles = {
    "Happy":    {"emoji": "😊", "color": (0, 255, 127)},     # spring green
    "Sad":      {"emoji": "😢", "color": (100, 149, 237)},   # cornflower blue
    "Angry":    {"emoji": "😠", "color": (255, 69, 0)},      # orange red
    "Surprised": {"emoji": "😲", "color": (255, 215, 0)},     # gold
    "Neutral":  {"emoji": "😐", "color": (200, 200, 200)},   # light gray
    "Fearful":     {"emoji": "😨", "color": (128, 0, 128)},     # purple
    "Disgusted":  {"emoji": "🤢", "color": (85, 107, 47)}      # dark olive green
}

#initialize no mood and time 
last_mood = None
last_speak_mood_time = time.time()


# Function to speak the detected mood
def speak_mood(mood):
    """Speak the detected mood using text-to-speech."""
    
    global last_speak_mood_time
    # Avoid speaking too frequently
    if time.time() - last_speak_mood_time > 3:
        threading.Thread(target=lambda: engine.say(f"Your mood is {mood}") or engine.runAndWait()).start()
        last_speak_mood_time = time.time()


def distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return np.linalg.norm(np.array([point1.x, point1.y]) - np.array([point2.x,point2.y]))

def calculate_mood(landmarks):
    """Calculate mood based on facial landmarks."""

    # Calculate distances between key points
    top_lip = landmarks[13] 
    bottom_lip = landmarks[15]   
    left_face_extreme = landmarks[234]  
    right_face_extreme = landmarks[454]
    left_eye_top = landmarks[159]
    left_eye_bottom = landmarks[145]
    right_eye_top = landmarks[386]
    right_eye_bottom = landmarks[374]
    mouth_left = landmarks[61]
    mouth_right = landmarks[291]
    iris_left = landmarks[468]
    
    
    # Calculate distances
    print("\n\n\nCalculating distances...")
    face_distance = distance(left_face_extreme, right_face_extreme)
    print("\nFace distance:", face_distance)
    open_mouth = distance(top_lip, bottom_lip) / face_distance
    print("\nOpen mouth:", open_mouth)
    stretched_mouth = distance(mouth_left, mouth_right) / face_distance
    print("\nStretched mouth:", stretched_mouth)
    open_eyes = (distance(left_eye_top, left_eye_bottom) + distance(right_eye_top, right_eye_bottom)) / (2 * face_distance)
    print("\nOpen eyes:", open_eyes)
    center_eye = (left_eye_top.y + left_eye_top.y + right_eye_top.y + right_eye_bottom.y) / 4
    print("\nCenter eye:", center_eye)
    sad_mood = iris_left.y - center_eye
    print("\nSad mouth:", sad_mood)
    
    
    # Determine mood based on distances
    if stretched_mouth > 0.40 and open_mouth < 0.06:
        return "Happy"
    elif sad_mood > 0.01 and open_eyes < 0.04:
        return "Sad"
    elif open_eyes > 0.096 and open_mouth < 0.06:
        return "Angry"
    elif open_mouth > 0.21:
        return "Surprised"
    elif 0.06 < open_mouth < 0.12:
        return "Fearful"
    elif open_mouth < 0.03 and open_eyes < 0.08 and stretched_mouth < 0.38:
        return "Disgusted"
    else:
        return "Neutral"

    
#initialize frame count
frame_count = 0

# set up video capture
cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video.")
    print("Please check your camera connection.")
    exit()
    

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Can't receive frame (Stream end!). Exiting...")
        break
    
    # Flip the frame horizontally and convert the frame to RGB
    frame = cv.flip(frame, 1) 
    
    a, b, c = frame.shape
    
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    canvas = np.zeros_like(frame)
    
    # Check if any face landmarks were detected
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            list_landmarks = face_landmarks.landmark            
            
            
            # Speak the mood if it has changed after 10 frames
            if frame_count % 10 == 0:
                emotion_labels = calculate_mood(list_landmarks) # Calculate mood
                
                if emotion_labels != last_mood:
                    print(f"Detected mood: {emotion_labels}")
                    speak_mood(emotion_labels)
                    last_mood = emotion_labels
                    
            else:
                last_mood = emotion_labels
            
            
            color = mood_styles[emotion_labels]["color"]
            emoji = mood_styles[emotion_labels]["emoji"]
            
            
            # Draw face mesh
            mp_drawing.draw_landmarks(
                image=canvas,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(color=color, thickness=1, circle_radius=1)
                )            
            
            # # Draw lips
            # mp_drawing.draw_landmarks(
            #     image=canvas,
            #     landmark_list=face_landmarks,
            #     connections=lips_connections,
            #     landmark_drawing_spec=None,
            #     connection_drawing_spec=mp_drawing.DrawingSpec(color=(128,128,128), thickness=1, circle_radius=1)
                # )
    
            # Draw irises
            for idx in LEFT_IRIS + RIGHT_IRIS:
                pt = list_landmarks[idx]
                cx, cy = int(pt.x * b), int(pt.y * a)
                cv.circle(canvas, (cx, cy), 2, (0, 255, 255), -1)
                
                
            # Display mood over the nose
            # cx, cy = int(list_landmarks[1].x * frame.shape[1]), int(list_landmarks[1].y * frame.shape[0])
            # cv.putText(canvas, f"{emotion_labels} {emoji}", (cx - 40, cy - 20),
            #         cv.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            
            # Display mood on the frame
            cv.putText(canvas, f'Mood: {emotion_labels}', (10, 30), 
                    cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            
        frame_count += 1
        
            
        # Resize both frames.
        frame_ = cv.resize(frame, (640, 480))
        canvas_= cv.resize(canvas, (640, 480))

        # Stack frames together
        frame_canvas = cv.hconcat([frame_, canvas_])
        
        # increase frame size
        frame_canvas = cv.resize(frame_canvas, (1280, 720))

        # Show windows
        # cv.imshow("Webcam Feed", frame_)
        # cv.imshow("Emotion Mesh", canvas_)
        cv.imshow("Combined Feed", frame_canvas)

        if cv.waitKey(1) == ord('q'):
            break
    
cap.release()
cv.destroyAllWindows()