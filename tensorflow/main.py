import numpy as np
import os
import PIL
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator


def plot_metric(history, metric):
    train_metrics = history.history[metric]
    val_metrics = history.history['val_' + metric]
    epochs = range(1, len(train_metrics) + 1)
    plt.plot(epochs, train_metrics)
    plt.plot(epochs, val_metrics)
    plt.title('Training and validation ' + metric)
    plt.xlabel("Epochs")
    plt.ylabel(metric)
    plt.legend(["train_" + metric, 'val_' + metric])
    plt.show()


callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, min_delta=0.005)

number_of_classes = 9
batch_size = 16
targetHeight = 100
targetWidth = 600
targetSize = (targetHeight, targetWidth)
src_path_train = 'dataset/train/'

model = Sequential([
    layers.Input(shape=(targetHeight, targetWidth, 1)),
    layers.experimental.preprocessing.Rescaling(1./255),
    layers.BatchNormalization(),
    layers.Conv2D(64, kernel_size=9, strides=3, padding='same', activation='relu'),
    layers.Conv2D(128, kernel_size=9, strides=3, padding='same', activation='relu'),
    layers.Dropout(0.1),
    layers.BatchNormalization(),
    layers.MaxPooling2D(3),
    layers.Dense(64),
    layers.Dense(20),
    layers.Flatten(),
    layers.Dense(number_of_classes, activation='softmax'),
])

train_datagen = ImageDataGenerator(
    rotation_range=0,
    zoom_range=0.00,
    width_shift_range=0.00,
    height_shift_range=0.00,
    shear_range=0.00,
    validation_split=0.20)

train_generator = train_datagen.flow_from_directory(
    directory=src_path_train,
    class_mode='categorical',
    target_size=targetSize,
    color_mode="grayscale",
    batch_size=batch_size,
    subset='training',
    shuffle=True,
    seed=3,
)

valid_generator = train_datagen.flow_from_directory(
    directory=src_path_train,
    class_mode='categorical',
    target_size=targetSize,
    color_mode="grayscale",
    batch_size=batch_size,
    subset='validation',
    shuffle=True,
    seed=3
)

print('Compiling model...')
model.compile(optimizer=keras.optimizers.Adam(),
              loss=[keras.losses.CategoricalCrossentropy(from_logits=True)],
              metrics=['categorical_accuracy'],
              )
print('Model compiled')

print('Training model...')
trainingHistory = model.fit(train_generator,
                            validation_data=valid_generator,
                            steps_per_epoch=train_generator.n // train_generator.batch_size,
                            validation_steps=valid_generator.n // valid_generator.batch_size,
                            epochs=45,
                            verbose=1,
                            # callbacks=[callback],
                            )
print('Model trained')

# To load model, use
# model = keras.models.load_model(pathToFolder)
print('---Saving model---')
model.save('laneDirectionModel/')

if input("Convert to Lite? [y/n]") in ('y', 'Y'):
    import convertToLite

    print('Converted')

plot_metric(trainingHistory, 'categorical_accuracy')
plot_metric(trainingHistory, 'loss')

# Insert Testing here
# ----------------------
print('-----Completed-----')
