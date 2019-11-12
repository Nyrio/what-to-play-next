import argparse
import csv
import random

from config import tags_to_features, feature_price, feature_achievements, \
    feature_controller


def get_args():
    parser = argparse.ArgumentParser(
        description='Generates the training and test sets.')
    parser.add_argument("test_ratio", type=float,
                        help="Ratio of samples to use as the test set"
                             " (between 0 and 1)")

    return parser.parse_args()


def main():
    args = get_args()

    with open('game_details.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        game_details = list(reader)
        details_dic = {detail[0]: detail[1:] for detail in game_details}
        del game_details

    with open('game_notes.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        game_notes = list(reader)

    total_set = [[note[0]] + details_dic[note[0]] + [note[1]]
                 for note in game_notes if note[0] in details_dic]
    all_ids = set(ts[0] for ts in total_set)
    test_ids = set(random.sample(all_ids, int(len(all_ids) * args.test_ratio)))

    test_set = [ts[1:] for ts in total_set if ts[0] in test_ids]
    training_set = [ts[1:] for ts in total_set
                    if ts[0] not in test_ids]
    random.shuffle(test_set)
    random.shuffle(training_set)

    with open("training_set.csv", "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerows(training_set)
    print("training_set.csv written")

    with open("test_set.csv", "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerows(test_set)
    print("test_set.csv written")

    inference_set = [details for key, details in details_dic.items()
                     if key not in all_ids]

    with open("inference_set.csv", "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerows(inference_set)
    print("inference_set.csv written")


main()
