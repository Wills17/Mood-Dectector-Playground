# import libraries
import os
import time
import cv2 as cv
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential 
from tensorflow.keras.utils import to_categorical 
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, BatchNormalization





# initializes list for images and label
data_train = "Face Expression Recognition Dataset/train/"
data_validate = "Face Expression Recognition Dataset/validation/"

# List for arrays
X_train = []
y_train = []
folders = ["surprise", "disgust", "happy", "sad", "fear", "neutral", "angry"]


# Load and append dataset for preprocessing
# Train folder
for folder in folders:
    train_path = data_train + folder
    print("\nCurrent folder:", train_path)
    for current_img in tqdm(os.listdir(train_path)):
        
        try:
            # Read and convert image to Grayscale
            img = cv.imread(train_path + "/" + current_img, cv.IMREAD_GRAYSCALE)
            
            # Display image
            # cv.imshow(f"Original Image {current_img}", img)
            # cv.waitKey(1000)
            
            # resize images
            img = cv.resize(img, (60, 60))
            
            # Show resized imaage
            # cv.imshow(f"Resized Image {current_img}", img)
            # cv.waitKey(1000)
            # cv.destroyAllWindows()
            
            X_train.append(img)
            y_train.append(folder)
            
        except:
            print(f"Error loading: {img}")
        
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


# yReshape and normalize
X_train = X_train.reshape(-1, 60, 60, 1).astype('float32') / 255.0
X_test = X_test.reshape(-1, 60, 60, 1).astype('float32') / 255.0


# Encode labels
encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train)
y_test = encoder.transform(y_test)

class_names = encoder.classes_
print("\nClasses:", class_names)

# Perform one hot encoding
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)



# Data augmentation
datagen = ImageDataGenerator(
    rotation_range=10,
    zoom_range=0.1,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

datagen.fit(X_train)


"""Start building model"""
model = Sequential()

# First layer
model.add(Conv2D(64, (3, 3), activation='relu', input_shape=(60, 60, 1)))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

# Second layer 
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

# Third layer 
model.add(Conv2D(256, (3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))


# Fully connected layer 
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.5))


# Output layer
model.add(Dense(y_train.shape[1], activation='softmax'))


# Compile with label smoothing
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss=CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy']
)

# Callbacks
callbacks = [
    ModelCheckpoint("emotions_model2.h5", monitor='val_accuracy', save_best_only=True, mode='max', verbose=1),
    EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6, verbose=1)
]


# Use augementation with training
history = model.fit(
    datagen.flow(X_train, y_train, batch_size=64),
    validation_data=(X_test, y_test),
    epochs=25,
    callbacks=callbacks,
    steps_per_epoch=len(X_train) // 64,
    verbose=1
)

print("Model Summary on version 2:\n")
model.summary()

