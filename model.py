import json
import pandas as pd
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import adagrad
from sklearn.preprocessing import LabelBinarizer
from sklearn.utils import shuffle

with open('work/facial_feats_data.json', 'r') as f:
    modeling_data = json.load(f)

targets = [i['celeb'] for i in modeling_data]
n_celebs = len(set(targets))

targets_as_categorical = LabelBinarizer().fit_transform(targets)
x = np.array([i['face_feats'] for i in modeling_data])

model = Sequential()
model.add(Dense(256, input_dim=x.shape[1], activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(n_celebs, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adagrad')

model.fit(x, targets_as_categorical, nb_epoch=25, shuffle=True, show_accuracy=True, validation_split=0.1)
