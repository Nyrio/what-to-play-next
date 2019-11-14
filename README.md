# What to play next?

Well, train a neural network to find out!

*Disclaimer: I am by no means an expert of Machine Learning so use my code at your own risk.*

## High level overview

You can check [the related blog post](https://nyri0.fr/en/blog/31).

## Requirements

I recommend using a Python virtualenv. Inside your virtualenv, use:
```bash
pip install -r requirements.txt
```

## How to prepare the dataset

 - Write your Steam API key in `api_keys.py`
 - **Configuration step:** Edit `config.py` with your custom settings. Very important step, see advice in the comments.
 - **Scraping step:** Run `download-data.py`. Use `--help` to see the options, which are useful e.g when the scraper crashed and you don't want to start from scratch. For me it took about 20 hours to scrape the data
 - **Annotation step:** create a file `game_notes.csv` with lines in the form: `<game-id>,<game-score>` with scores between 0 and 1 and game IDs that are in `game_details.csv` generated at the previous step. You can see the associations ID-name in `game_list.csv`. *Note: `game_details.csv` has only a subset of the games found in `game_list.csv` because games without a Metacritic score were discarded*. You should have as many games that you like as games that you don't like in the training set. You can use `random_games.py` to generate a random sample, check them in the Store and add them with a bad score if you think you wouldn't like them.
 - Run `build_sets.py` to generate the training and inference sets

## How to train and predict

 - Edit the model in `neural_network.py` if you wish
 - **Training step:** Call `neural_network.py` with the command `train` to train the network. You can use `-p` to plot a training curve. Check if you are overfitting, underfitting, etc. You can run training multiple times until it looks good, with a small training set I have observed wide variance between the results from one execution to another. You can control the number of iterations with `-i`
 - **Prediction step:** Call `neural_network.py` with the command `fit`
 - Check the predictions in `recommended.csv`
 - Play videogames
