# import libraries
import os
import time
import cv2 as cv
import numpy as np
from tqdm import tqdm
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical 
from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, BatchNormalization



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
    print("\nCurrent folder:", train_path)
    for current_img in tqdm(os.listdir(train_path)):
        
        # Read and convert image to Grayscale
        img = cv.imread(train_path + "/" + current_img, cv.IMREAD_GRAYSCALE)
        
        # Display image
        # cv.imshow(f"Original Image {current_img}", img)
        # cv.waitKey(1000)
        
        # resize images
        img = cv.resize(img, (150, 150))
        
        # Show resized imaage
        # cv.imshow(f"Resized Image {current_img}", img)
        # cv.waitKey(1000)
        # cv.destroyAllWindows()
        
        X_train.append(img)
        y_train.append(folder)
        
    print("Appended all images in {} folder successfully.".format(folder))
    
print(f"\nFinished processing all images in the folders successfully.")


# Convert to numpy array
X_train = np.array(X_train)
y_train = np.array(y_train)


# Confirm length and splt into test and train
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=32)
print("\nShape of X_train:", X_train.shape)
print("Shape of y_train:", y_train.shape)
print("Shape of X_test:", X_test.shape)
print("Shape of y_test:", y_test.shape)


# # Reshape and normalize
# X_train = X_train.reshape(-1, 150, 150, 1) / 255.0
# X_test = X_test.reshape(-1, 150, 150, 1) / 255.0


# Encode labels
encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train)
y_test = encoder.transform(y_test)

# One-hot encode for y_train
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)

# Print classses
print("\nClasses:", encoder.classes_)


"""Start building model"""
# Call Sequential for CNN building
model = Sequential()

# First layer with 64 NNs
model.add(Conv2D(64, (3, 3), activation = "relu", input_shape=(150, 150, 1)))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

# Second layer with 128 NNs
model.add(Conv2D(128, (3, 3), activation = "relu"))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

# third layer with 256 NNs
model.add(Conv2D(256, (3,3), activation = "relu"))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))


# Fourth layer (fully connected)
model.add(Flatten())
model.add(Dense(512, activation = "relu"))
# avod overfitting
model.add(Dropout(0.5)) 


# Output layer
model.add(Dense(y_train.shape[1], activation="softmax"))  


