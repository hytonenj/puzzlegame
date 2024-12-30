# filepath: /home/hytonenj/puzzlegame/game/levels.py
import json
from game.block import Block
from game.level import Level

def load_levels_from_json(file_path, block_size):
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

def create_levels(block_size):
    return load_levels_from_json('/home/hytonenj/puzzlegame/data/levels.json', block_size)