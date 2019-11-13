import argparse
import csv
import functools
import matplotlib.pyplot as plt

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras import regularizers

from config import hidden_layer_size, n_params


def load_dataset(file_path):
    print("Loading {}".format(file_path))
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        csv_data = np.array([list(map(float, line)) for line in reader])

    return csv_data


def get_model():
    model = tf.keras.Sequential([
        Dense(hidden_layer_size, input_shape=(n_params,),
              kernel_regularizer=regularizers.l2(0.001)),
        Activation('relu'),
        Dense(hidden_layer_size, kernel_regularizer=regularizers.l2(0.001)),
        Activation('relu'),
        Dense(1),
        Activation('sigmoid')
    ])

    model.compile(optimizer="rmsprop", loss='mse', metrics=['mse'])

    return model


def get_args():
    parser = argparse.ArgumentParser(
        description='Training or inference using a neural network model.')
    parser.add_argument("-p", "--plot", action="store_true",
                        help="Save training curve in a picture")
    parser.add_argument("-w", "--weights", default="weights.h5",
                        help="File to hold the weights")
    parser.add_argument("-i", "--iterations", type=int, default=250,
                        help="Number of iterations (epochs)")
    parser.add_argument("command", choices=["fit", "predict"],
                        help="Fit the model or predict")

    return parser.parse_args()


def main():
    args = get_args()
    model = get_model()

    if args.command == "fit":
        training_csv = load_dataset("training_set.csv")
        np.random.shuffle(training_csv)
        training_data = training_csv[:, :-1]
        training_labels = training_csv[:, -1]

        history = model.fit(training_data, training_labels, epochs=args.iterations,
                            verbose=2, validation_split=0.3, shuffle=True)

        if args.plot:
            plt.plot(history.history['mse'])
            plt.plot(history.history['val_mse'])
            plt.title('training curve')
            plt.ylabel('mean squared error')
            plt.xlabel('epoch')
            plt.legend(['train', 'test'], loc='upper right')
            plt.savefig("training_curve.png")
            print("Training curve saved in training_curve.png")

        model.save_weights(args.weights)
        print("Weights saved in {}".format(args.weights))

    elif args.command == "predict":
        print("Loading weights from {}".format(args.weights))
        model.load_weights(args.weights)

        inference_csv = load_dataset("inference_set.csv")
        inference_features = inference_csv[:, 1:]

        print("Starting inference")
        predictions = model.predict_on_batch(inference_features).numpy()

        with open('game_list.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)
            game_list = list(reader)
            names_dic = {int(detail[0]): detail[1] for detail in game_list}
            del game_list

        id_score = sorted(([int(inference_csv[i, 0]), predictions[i, 0]]
                           for i in range(inference_csv.shape[0])),
                          key=lambda x: -x[1])
        for i in range(len(id_score)):
            id_score[i].append(names_dic[id_score[i][0]])

        with open("recommended.csv", "w") as csv_file:
            writer = csv.writer(csv_file, lineterminator="\n")
            writer.writerows(id_score)
        print("Results written in recommended.csv")

    else:
        print("Unrecognized command: {}".format(args.command))
        exit(1)


main()
