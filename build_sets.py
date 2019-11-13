import argparse
import csv
import random


def main():
    with open('game_details.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        game_details = list(reader)
        details_dic = {detail[0]: detail[1:] for detail in game_details}
        del game_details

    with open('game_notes.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        game_notes = list(reader)

    all_ids = set(note[0] for note in game_notes
                  if note[0] in details_dic)
    training_set = [details_dic[note[0]] + [note[1]]
                    for note in game_notes if note[0] in all_ids]

    random.shuffle(training_set)

    with open("training_set.csv", "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerows(training_set)
    print("training_set.csv written")

    inference_set = [[key] + details for key, details in details_dic.items()
                     if key not in all_ids]

    with open("inference_set.csv", "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerows(inference_set)
    print("inference_set.csv written")


main()
