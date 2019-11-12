# This file allows customization of the model, adapted to your own tastes.

# Number of neurons in the hidden layer
hidden_layer_size = 16
nn_iterations = 1000

# The following tags will be added as features in the dataset.
# Find popular tags here: https://steamdb.info/tags/
# Notes:
#  - a relevant tag can be both a positive or a negative one
#  - very generic tags are unlikely to be relevant (e.g "action")
#  - the more features you add, the greater is the risk of overfitting.
tags_to_features = [
    # positive tags
    "Story Rich",
    "Great Soundtrack",
    "Atmospheric",
    # negative tags (don't judge me please)
    "Anime",
    "Strategy",
    "Shooter",
]

# Do you care about the price when buying games?
feature_price = False

# Do you care about controller support?
feature_controller = True

# Do you care about achievements?
feature_achievements = False

n_params = len(tags_to_features) + feature_price + \
    feature_controller + feature_achievements + 4
