# Facial and mood dectection using OpenCV and mediapipe

#Import necessary libraries
import cv2 as cv
import mediapipe as mp
import numpy as np


# set up mediapipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5, # detect up to 5 faces
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    refine_landmarks=True)

# set up mediapipe drawing utils
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
lips_connections = mp_face_mesh.FACEMESH_LIPS
LEFT_IRIS = [468, 469, 470, 471]
RIGHT_IRIS = [473, 474, 475, 476]


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
    print("\n\n\nFace distance:", face_distance)
    open_mouth = distance(mouth_left, mouth_right) / face_distance
    print("\nOpen mouth:", open_mouth)
    stretched_mouth = distance(top_lip, bottom_lip) / face_distance
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
    elif open_mouth > 0.25:
        return "Surprised"
    elif 0.06 < open_mouth < 0.12:
        return "Fearful"
    elif open_mouth < 0.03 and open_eyes < 0.08 and stretched_mouth < 0.38:
        return "Disgusted"
    else:
        return "Neutral"

    
    

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
            
            # Calculate mood
            emotion_labels = calculate_mood(list_landmarks)
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
            
            # Draw lips
            mp_drawing.draw_landmarks(
                image=canvas,
                landmark_list=face_landmarks,
                connections=lips_connections,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(128,128,128), thickness=1, circle_radius=1)
                )
    
            # Draw irises
            for idx in LEFT_IRIS + RIGHT_IRIS:
                pt = list_landmarks[idx]
                cx, cy = int(pt.x * b), int(pt.y * a)
                cv.circle(canvas, (cx, cy), 2, (0, 255, 255), -1)
            
            
            # Display mood on the frame
            cv.putText(canvas, f'Mood: {emotion_labels}', (10, 30), 
                        cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            
        # Resize both frames.
        frame_ = cv.resize(frame, (512, 384))
        canvas_= cv.resize(canvas, (512, 384))

        # Show windows
        cv.imshow("Webcam Feed", frame_)
        cv.imshow("Emotion Mesh", canvas_)

        if cv.waitKey(1) == ord('q'):
            break
    
cap.release()
cv.destroyAllWindows()