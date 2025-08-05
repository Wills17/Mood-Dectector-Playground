# import libraries
import os
import cv2 as cv
import numpy as np
# from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import time
from tqdm import tqdm


# initializes list for images and label
data_train = "Face Expression Recognition Dataset/train/"
data_validate = "Face Expression Recognition Dataset/validation/"

# List for arrays
X_train = []
y_train = []
folders = ['surprise', 'disgust', 'happy', 'sad', 'fear', 'neutral', 'angry']


# Load and append dataset for preprocessing
# Train folder
for folder in folders:
    train_path = data_train + folder
    print("\nCurrent folder:", folder)
    for current_img in tqdm(os.listdir(train_path)):
        
        # Read and convert image to Grayscale
        img = cv.imread(train_path + "/" + current_img, cv.IMREAD_GRAYSCALE)
        
        # Display image
        cv.imshow(f"Original Image {current_img}", img)
        cv.waitKey(1000)
        
        # resize images
        img = cv.resize(img, (250, 250))
        
        # Show resized imaage
        cv.imshow(f"Resized Image {current_img}", img)
        cv.waitKey(1000)
        cv.destroyAllWindows()
        
        X_train.append(img)
        y_train.append(folder)
        
    print("Appended all images in {} folder successfully.".format(folder))
    
print(f"\nAppended all images in the Training folder successfully.")
