# Facial and mood dectection using OpenCV and mediapipe

#import necessary libraries
import cv2
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

#connections for left and right eyes
left_eye_connections = mp_face_mesh.FACEMESH_LEFT_EYE
right_eye_connections = mp_face_mesh.FACEMESH_RIGHT_EYE


# Labels for emotions
emotion_labels =    \
    ['Neutral', 'Happy', 'Sad', 'Angry', 'Surprised', 'Disgusted', 'Fearful']



def distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return np.linalg.norm(np.array(point1.x, point1.y) - np.array(point2.x,point2.y))

def calculate_mood(landmarks):
    """Calculate mood based on facial landmarks."""
    if not landmarks:
        return "Neutral"

    # Calculate distances between key points
    top_lip = landmarks[0] 
    bottom_lip = landmarks[17]   
    left_eye_extreme = landmarks[230]  # left eye extreme point
    right_eye_extreme = landmarks[450]  # right eye extreme point
    left_eye_top = landmarks[159]
    left_eye_bottom = landmarks[145]
    right_eye_top = landmarks[386]
    right_eye_bottom = landmarks[374]
    mouth_left = landmarks[61]
    mouth_right = landmarks[291]


    #check if landmarks are valid
    if not (left_eye_bottom and right_eye_bottom and 
            top_lip and bottom_lip and left_eye_top and 
            right_eye_top and mouth_left and mouth_right):
        return "Neutral"
    
    
    # Calculate distances
    face_distance = distance(left_eye_extreme, right_eye_extreme)
    print("Face distance:", face_distance)
    open_mouth = distance(mouth_left, mouth_right) / face_distance
    print("Open mouth:", open_mouth)
    stretched_mouth = distance(top_lip, bottom_lip) / face_distance
    print("Stretched mouth:", stretched_mouth)
    open_eyes = distance(left_eye_top, left_eye_bottom) + distance(right_eye_top, right_eye_bottom) / (2 * face_distance)
    print("Open eyes:", open_eyes)
    center_eye = (left_eye_top.y + right_eye_top.y + right_eye_top.y + right_eye_bottom.y) / 4
    print("Center eye:", center_eye)
    sad_mouth = distance(top_lip, bottom_lip) / face_distance
    print("Sad mouth:", sad_mouth)
    
    
    # Determine mood based on distances
    if open_mouth > 0.1 and stretched_mouth > 0.4:
        return "Happy"
    elif open_mouth > 0.06 and open_mouth < 0.12:
        return "Fearful"
    elif open_eyes < 0.05 and sad_mouth < 0.1:
        return "Sad"
    elif open_mouth > 0.12:
        return "Suprised"
    elif open_mouth < 0.03 and open_eyes > 0.08 and stretched_mouth < 0.4:
        return "Disgusted"
    elif open_mouth > 0.09 and open_mouth < 0.05:
        return "Angry"
    else:
        return "Neutral"
    

# set up video capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video.")
    print("Please check your camera connection.")
    exit()
    

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Can't receive frame (Stream end!). Exiting...")
        break

    cv2.imshow('Camera Feed', frame)

    if cv2.waitKey(1) == ord('q'):
        break
    
    
    
    
    
    
cap.release()
cv2.destroyAllWindows()