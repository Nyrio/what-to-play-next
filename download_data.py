#!/usr/bin/env python3

import codecs
import http.client
import json
from time import sleep

from api_keys import api_key


def request_wrapper(conn, request):
    for _ in range(10):
        conn.request("GET", request)
        res = conn.getresponse()

        if res.status == 200:
            return res.read()
    else:
        print("API call failed 10 times, aborting")
        exit(1)


def download_list(conn):
    games = []

    print("Downloading the list of apps from the store...")

    have_more_results = True
    last = None
    while have_more_results:
        request = (
            "/IStoreService/GetAppList/v1/?key={key}{last_appid_param}"
            "".format(key=api_key,
                      last_appid_param=("&last_appid={}".format(last)
                                        if last else "")))
        raw_data = request_wrapper(conn, request)
        data = json.loads(raw_data)["response"]

        for app in data["apps"]:
            games.append([app["appid"], app["name"]])
        have_more_results = "have_more_results" in data and data["have_more_results"]
        if have_more_results:
            last = data["last_appid"]

        print("Downloaded: {}".format(len(games)), end="\r", flush=True)
    print("\n")

    return games


def main():
    conn = http.client.HTTPSConnection("api.steampowered.com")
    games = download_list(conn)
    conn.close()

    with codecs.open("games.csv", "w", encoding="utf-8") as games_csv:
        games_csv.write("\n".join(",".join(map(str, game)) for game in games))

    print("Dataset written in games.csv")


main()
