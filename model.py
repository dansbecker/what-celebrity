import json
import pandas as pd
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential, model_from_json
from keras.callbacks import EarlyStopping
from keras.layers import Dense, Dropout, Flatten, Convolution1D, Convolution2D, MaxPooling2D, Convolution3D
from keras.layers.noise import GaussianNoise
from keras.objectives import categorical_crossentropy
from keras.optimizers import Adagrad, Adam, Adamax, RMSprop
from keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import shuffle
from sklearn.cross_validation import train_test_split

def model_from_thumbnails(train_x, train_y, val_x, val_y):
    n_obs, n_channels, n_rows, n_cols = train_x.shape
    n_classes = y.shape[1]

    model = Sequential()
    model.add(Convolution2D(32, 2, 2, border_mode='valid',
                            activation='relu',
                            input_shape=(n_channels, n_rows, n_cols)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Convolution2D(64, 2, 2, border_mode='valid',
                            activation='relu'))
    model.add(Convolution2D(64, 2, 2, border_mode='valid',
                            activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Convolution2D(64, 2, 2, border_mode='valid',
                            activation='relu'))

    model.add(Flatten())
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(n_classes, activation='softmax'))
    optimizer = Adam()
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    stopper = EarlyStopping(monitor='val_loss', patience=15, verbose=0, mode='auto')

    model.fit(train_x, train_y, shuffle=True,
                        nb_epoch=100, validation_data=(val_x, val_y),
                        callbacks = [stopper])
    return model

if __name__ == "__main__":
    loaded_file = np.load("work/thumbnail_px_and_targ.npy.npz")
    x = loaded_file['x'] / 255
    x = x.swapaxes(1,3).swapaxes(2,3)
    y = LabelBinarizer().fit_transform(loaded_file['y'])
    train_x, val_x, train_y, val_y = train_test_split(x, y,
                                                      test_size=0.10, random_state=80401)

    model = model_from_thumbnails(train_x, train_y, val_x, val_y)
    print('Saving Model...')
    json_string = model.to_json()
    open('my_model_architecture.json', 'w').write(json_string)
    model.save_weights('my_model_weights.h5', overwrite=True)

    print('Reloading Model...')
    model = model_from_json(open('my_model_architecture.json').read())
    model.load_weights('my_model_weights.h5')
