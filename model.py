import json
import pandas as pd
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.layers.noise import GaussianNoise
from keras.optimizers import Adagrad, Adam, Adamax, RMSprop
from keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import shuffle
from sklearn.cross_validation import train_test_split

    # Models from facial_feats_data.json (indico )facial featurizations api didn't work well
    # cross-entropy error ~5, and accuracy ~ 0.5%)
    # training data for those models is in


def model_from_thumbnails(val_size = 500):
    loaded_file = np.load("work/thumbnail_px_and_targ.npy.npz")
    x = loaded_file['x'] / 255
    y = LabelBinarizer().fit_transform(loaded_file['y'])
    train_x, val_x, train_y, val_y = train_test_split(x, y,
                                                      test_size=0.10, random_state=80401)

    n_obs, img_rows, img_cols, n_channels = train_x.shape
    n_classes = y.shape[1]

    model = Sequential()
    model.add(Convolution2D(6, 2, 2, border_mode='same',
                            dim_ordering='tf', activation='relu',
                            input_shape=(img_rows, img_cols, n_channels)))
    model.add(Convolution2D(6, 3, 3, border_mode='same',
                            dim_ordering='tf', activation='relu'))
    #model.add(MaxPooling2D(pool_size=(2, 2), dim_ordering='tf'))
    #model.add(Dropout(0.4))
    #model.add(Convolution2D(6, 3, 3, border_mode='same',
    #                        dim_ordering='tf', activation='relu'))
    #model.add(MaxPooling2D(pool_size=(2, 2)))
    #model.add(Dropout(0.4))
    model.add(Flatten())
    model.add(Dense(150, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(n_classes, activation='softmax'))
    optimizer = Adam() #could use clipnorm
    model.compile(loss='categorical_crossentropy', optimizer=optimizer)

    data_feeder = ImageDataGenerator(featurewise_center=True,
                                     featurewise_std_normalization=True,
                                     horizontal_flip=True,
                                     width_shift_range=0.1,
                                     height_shift_range=0.1
                                     )
    data_feeder.fit(x)
    model.fit_generator(data_feeder.flow(train_x, train_y, batch_size=32),
                        nb_epoch=22,
                        samples_per_epoch=n_obs,
                        show_accuracy=True,
                        validation_data=(val_x, val_y))

if __name__ == "__main__":
    model_from_thumbnails()
