import os
import json
from game.block import Block
from game.level import Level
from game.teleport import TeleportPair

def load_levels_from_json(file_path):
    with open(file_path, 'r') as f:
        levels_data = json.load(f)

    levels = []
    for level_data in levels_data:
        player_start = tuple(level_data["player_start"])
        key_start = tuple(level_data["key_start"])
        door_start = tuple(level_data["door_start"])
        blocks = [Block(*block) for block in level_data["blocks"]]
        teleports = [TeleportPair(teleport[0][0], teleport[0][1], teleport[1][0], teleport[1][1], 80, 80) for teleport in level_data.get("teleports", [])]
        levels.append(Level(player_start, key_start, door_start, blocks, teleports))
    return levels

def create_levels(path):
    return load_levels_from_json(os.path.join(os.path.dirname(__file__), path))