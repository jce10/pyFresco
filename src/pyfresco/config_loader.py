import json
from pathlib import Path

"""

Module that loads the reaction configuration from a JSON file.

Parameters:
- config_path (str or Path): Path to the JSON config file.

Returns:
- dict: A dictionary containing all reaction parameters.

"""
def load_reaction_config(config_path):
    config_path = Path(config_path).expanduser()

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as file:
        return json.load(file)