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

