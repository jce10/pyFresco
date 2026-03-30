from pathlib import Path

# This file lives in: pyFRESCO/src/pyfresco/config.py
# parents[0] = pyfresco
# parents[1] = src
# parents[2] = pyFRESCO (project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = PROJECT_ROOT / "config"
INPUTS_DIR = PROJECT_ROOT / "inputs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

REACTION_CONFIG_FILE = CONFIG_DIR / "reaction_config.json"
INPUT_GENERATOR_FILE = INPUTS_DIR / "input_generator.inp"
