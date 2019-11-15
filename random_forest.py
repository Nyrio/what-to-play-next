import argparse
import csv
import matplotlib.pyplot as plt
import pickle

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics


def load_dataset(file_path):
    print("Loading {}".format(file_path))
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        csv_data = np.array([list(map(float, line)) for line in reader])

    return csv_data



def get_args():
    parser = argparse.ArgumentParser(
        description='Training or inference using a neural network model.')
    parser.add_argument("-f", "--forest-file", default="forest.sav",
                        help="File where to save your forest")
    parser.add_argument("-t", "--trees", type=int, default=20,
                        help="Number of decision trees in the forest")
    parser.add_argument("command", choices=["fit", "predict"],
                        help="Fit the model or predict")

    return parser.parse_args()


def main():
    args = get_args()

    if args.command == "fit":
        training_csv = load_dataset("training_set.csv")
        np.random.shuffle(training_csv)
        training_data = training_csv[:, :-1]
        training_labels = training_csv[:, -1]

        X_train, X_test, y_train, y_test = train_test_split(
            training_data, training_labels, test_size=0.3)

        print("Starting taining")
        regressor = RandomForestRegressor(n_estimators=args.trees)
        regressor.fit(X_train, y_train)

        print("Starting evaluation")
        y_pred = regressor.predict(X_test)
        print('MSE:', metrics.mean_squared_error(y_test, y_pred))

        pickle.dump(regressor, open(args.forest_file, 'wb'))

    elif args.command == "predict":
        regressor = pickle.load(open(args.forest_file, 'rb'))

        inference_csv = load_dataset("inference_set.csv")
        inference_features = inference_csv[:, 1:]

        print("Starting inference")
        predictions = regressor.predict(inference_features)

        with open('game_list.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)
            game_list = list(reader)
            names_dic = {int(detail[0]): detail[1] for detail in game_list}
            del game_list

        id_score = sorted(([int(inference_csv[i, 0]), predictions[i]]
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
