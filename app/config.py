from pathlib import Path

import yaml

CONFIG_PATH = Path("config/portal.yaml")

with open(CONFIG_PATH, "r") as f:
    settings = yaml.safe_load(f)
