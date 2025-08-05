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
data_train = "Face Expression Recognition Dataset/images/train/"
data_validate = "Face Expression Recognition Dataset/images/train/"
