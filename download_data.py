#!/usr/bin/env python3

import argparse
import codecs
import csv
import math
import os
import sys
import time

from currency_converter import CurrencyConverter
import requests

from api_keys import api_key
from config import tags_to_features, feature_price, feature_controller, \
    feature_achievements


# Parameters of this scraper
batch_size = 25
all_commands = ["all",
                "download-list",
                "clear-list",
                "download-details",
                "clear-details"]


def request_wrapper(url, parameters=None):
    """Return json response of a GET request
    """
    try:
        res = requests.get(url=url, params=parameters)
    except Exception as e:
        print('Exception:', e)

        for _ in range(5, 0, -1):
            time.sleep(1)

        return request_wrapper(url, parameters)

    if res:
        return res.json()
    else:
        time.sleep(10)
        return request_wrapper(url, parameters)


def download_list():
    """TODO: doc
    """
    game_list = []

    have_more_results = True
    last = None
    while have_more_results:
        url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
        params = {"key": api_key, "max_results": 1000}
        if last:
            params["last_appid"] = last
        data = request_wrapper(url, params)["response"]

        for app in data["apps"]:
            game_list.append([app["appid"], app["name"]])
        have_more_results = ("have_more_results" in data
                             and data["have_more_results"])
        if have_more_results:
            last = data["last_appid"]

        print("Games listed: {}".format(len(game_list)), end="\r", flush=True)

    with open("game_list.csv", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerows(game_list)
    print("\nList of games written in game_list.csv\n---")

    return game_list


def download_details(game_list, batch_id=0):
    """TODO: doc
    """
    conv = CurrencyConverter()
    game_details = []
    failures = 0
    discarded = 0

    filters_ = ["metacritic", "release_date", "categories"]
    if feature_price:
        filters_.append("price_overview")
    filters = ",".join(filters_)

    print("Batch #{}".format(batch_id))

    for i in range(batch_id * batch_size,
                   min((batch_id + 1) * batch_size, len(game_list))):
        game_id = game_list[i][0]

        url_store = "https://store.steampowered.com/api/appdetails"
        params_store = {"appids": game_id, "filters": filters}

        url_steamspy = "https://steamspy.com/api.php"
        params_steamspy = {"request": "appdetails", "appid": game_id}

        data_store = request_wrapper(url_store, params_store)[str(game_id)]
        data_steamspy = request_wrapper(url_steamspy, params_steamspy)

        # The API query failed
        if not data_store["success"]:
            failures += 1
            continue
        data = data_store["data"]

        # Discard the games that are missing some information
        if "metacritic" not in data \
           or data["release_date"]["coming_soon"]:
            discarded += 1
            continue

        details = [game_id]

        # If configured so, convert the price to a common unit and add it
        # to the features. Note: the API gives the price in cents
        if feature_price:
            details.append(
                0 if "price_overview" not in data
                else conv.convert(
                    data["price_overview"]["initial"],
                    data["price_overview"]["currency"]) / 10000)

        # Normalized metacritic score
        details.append(data["metacritic"]["score"] / 100)

        # Get and parse the categories
        categories = ({cat["id"] for cat in data["categories"]}
                      if "categories" in data else {})
        if feature_achievements:
            details.append(int(22 in categories))
        if feature_controller:
            details.append(int(28 in categories))
        details.append(int(2 in categories))  # single-player

        # Get and parse the relevant tags
        if len(data_steamspy["tags"]) > 0:
            tags_view = data_steamspy["tags"].items()
            # Heuristics: only select tags that have at least 42% as many
            # votes as the tag with the most votes
            max_votes = max(v for k, v in tags_view)
            tags = set(k for k, v in tags_view if v >= 0.42 * max_votes)
            for tag in tags_to_features:
                details.append(int(tag in tags))
        else:
            details += [0] * len(tags_to_features)

        # Ratio of positive/negative reviews
        positive = data_steamspy["positive"]
        negative = data_steamspy["negative"]
        details.append(round(positive / max(1, positive + negative), 2))

        # Game release date, normalized between 1997 and 2027
        try:
            release_year = int(data["release_date"]["date"][-4:])
        except:
            release_year = 2012  # default value in case of failure
        details.append(max(0, min(1, round((release_year - 1997) / 30, 2))))

        game_details.append(details)
        print("Details downloaded: {dl} ; discarded: {ds} ;"
              " non-accessible: {fl}".format(
                  dl=len(game_details), ds=discarded, fl=failures), end="\r", flush=True)
    print("Details downloaded: {dl} ; discarded: {ds} ;"
          " non-accessible: {fl}".format(
              dl=len(game_details), ds=discarded, fl=failures), end="\r", flush=True)
    
    with open("game_details.csv", "a", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerows(game_details)
    print("\nBatch #{} added in game_details.csv\n---".format(batch_id))


def get_args():
    parser = argparse.ArgumentParser(description='Build the dataset.')
    parser.add_argument("-b", "--batch", type=int, metavar="id", default=0,
                        help=("For the download-details step, continue at the"
                              " given batch id (in case of interruption)"))
    parser.add_argument("command", nargs="+", choices=all_commands,
                        help="Which action/step to execute")

    return parser.parse_args()


def main():
    args = get_args()

    commands = set(args.command)
    if "all" in commands:
        commands = all_commands

    if "clear-list" in commands:
        if os.path.isfile("game_list.csv"):
            os.remove("game_list.csv")
            print("game_list.csv removed\n---")
        else:
            print("game_list.csv doesn't exist yet\n---")

    if "download-list" in commands:
        print("Downloading the list of games from the store...")
        game_list = download_list()
    else:
        with open('game_list.csv', 'r', encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            game_list = list(reader)

    if "clear-details" in commands \
       or ("download-details" in commands and args.batch == 0):
        if os.path.isfile("game_details.csv"):
            os.remove("game_details.csv")
            print("game_details.csv removed\n---")
        else:
            print("game_details.csv doesn't exist yet\n---")

    if "download-details" in commands:
        print("Downloading game details from the store...")
        for bi in range(args.batch, math.ceil(len(game_list) / batch_size)):
            download_details(game_list, bi)


main()
