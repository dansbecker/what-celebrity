import json
import pandas as pd
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers.convolutional import Convolution1D, Convolution2D, MaxPooling2D, Convolution3D
from keras.layers.noise import GaussianNoise
from keras.objectives import categorical_crossentropy
from keras.optimizers import Adagrad, Adam, Adamax, RMSprop
from keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import shuffle
from sklearn.cross_validation import train_test_split


def model_from_thumbnails(train_x, val_x, train_y, val_y):
    n_obs, n_rows, n_cols, n_channels = train_x.shape
    n_classes = y.shape[1]

    model = Sequential()
    model.add(Convolution2D(3, 1, 1, init="glorot_uniform",
                            activation='relu', border_mode='valid',
                            dim_ordering='th',
                            input_shape=(n_rows, n_cols, n_channels)))
    model.add(Convolution2D(8, 2, 2, border_mode='same', init="glorot_uniform",
                            dim_ordering='th', activation='relu',
                            input_shape=(n_rows, n_cols)))
    model.add(MaxPooling2D(pool_size=(2, 2), dim_ordering='th'))
    model.add(Convolution2D(16, 2, 2, border_mode='same', init="glorot_uniform",
                            dim_ordering='th', activation='relu'))
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(n_classes, activation='softmax'))
    optimizer = Adam()
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    model.fit(train_x, train_y, batch_size=32, nb_epoch=15, shuffle=True, validation_data=(val_x, val_y))
    val_preds = model.predict_proba(val_x)
    # model.loss returns tensor from the backend
    val_loss = model.loss(val_y, val_preds).eval().mean()
    return val_loss


if __name__ == "__main__":
    loaded_file = np.load("work/thumbnail_px_and_targ.npy.npz")
    x = loaded_file['x'] / 255
    x = x.swapaxes(1,3).swapaxes(2,3)
    y = LabelBinarizer().fit_transform(loaded_file['y'])
    train_x, val_x, train_y, val_y = train_test_split(x, y,
                                                      test_size=0.10, random_state=80401)
    model_from_thumbnails(train_x, val_x, train_y, val_y)
