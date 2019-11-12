import csv
import functools

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Activation

from config import hidden_layer_size, n_params, nn_iterations
 

def load_dataset(file_path):
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        csv_data = np.array([list(map(float, line)) for line in reader])

    return csv_data


def get_model():
    model = tf.keras.Sequential([
        Dense(hidden_layer_size, input_shape=(n_params,)),
        Activation('relu'),
        Dense(1),
        Activation('relu')
    ])

    model.compile(optimizer="rmsprop", loss='mse')

    return model


def main():
    training_csv = load_dataset("training_set.csv")
    training_data = training_csv[:, :-1]
    training_labels = training_csv[:, -1]

    # Giving higher weights to games with a really good grade
    training_weights = 1 + (training_labels >= 0.85)

    model = get_model()

    model.fit(training_data, training_labels, epochs=nn_iterations,
              verbose=2, validation_split=0.2, shuffle=True)


main()
