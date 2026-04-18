"""

Module that loads the reaction configuration from a JSON file.

Parameters:
- config_path (str or Path): Path to the JSON config file.

Returns:
- dict: A dictionary containing all reaction parameters.

"""

from rich.console import Console
import json
from pathlib import Path

console = Console()


def load_reaction_config(config_path):
    config_path = Path(config_path).expanduser()
    console.print(f"[blue]Loading reaction configuration from: {config_path}[/]")

    if not config_path.exists():
        raise FileNotFoundError(f"[red] Config file not found: {config_path}[/]")

    with open(config_path, "r") as file:
        return json.load(file)