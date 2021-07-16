import tensorflow as tf
from tensorflow import keras
import numpy as np
from cv2 import imread, IMREAD_GRAYSCALE

pathToFolder = 'laneDirectionModel/'
model = keras.models.load_model(pathToFolder)
model.summary()
image = imread('test.jpg', IMREAD_GRAYSCALE)
image = np.expand_dims(image, -1)
image = np.expand_dims(image, 0)
predictions = model.predict(image, verbose=1)
print(predictions)