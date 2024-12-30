import os
import json
from game.block import Block
from game.level import Level

def load_levels_from_json(file_path):
    with open(file_path, 'r') as f:
        levels_data = json.load(f)

    levels = []
    for level_data in levels_data:
        player_start = tuple(level_data["player_start"])
        key_start = tuple(level_data["key_start"])
        door_start = tuple(level_data["door_start"])
        blocks = [Block(*block) for block in level_data["blocks"]]
        levels.append(Level(player_start, key_start, door_start, blocks))

    return levels

def create_levels():
    return load_levels_from_json(os.path.join(os.path.dirname(__file__), '../data/levels.json'))