import argparse
import csv
import random


def get_args():
    parser = argparse.ArgumentParser(
        description='Generates a random sample of games.')
    parser.add_argument("size", type=int, help="Number of games to pick")

    return parser.parse_args()


def main():
    args = get_args()
    
    with open('game_list.csv', 'r', encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        game_list = list(reader)

    with open('game_details.csv', 'r', encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        game_details = list(reader)

    id_with_details = set(gd[0] for gd in game_details)
    id_to_name = {gl[0]: gl[1] for gl in game_list}

    selected_ids = random.sample(id_with_details, args.size)

    for id in selected_ids:
        print("#{}: {}".format(id, id_to_name[id]))


main()
