import json
from app.models import Player


def modelize(player_one: dict, player_two: dict):
    with open("handicap.json", "r") as json_file:
        data = json.load(json_file)
        p1 = Player(**player_one)
        p2 = Player(**player_two)
        print(type(p1), type(p2))
        p1.handicap = data.get(p1.lichess, False)
        p2.handicap = data.get(p2.lichess, False)
    return p1, p2
