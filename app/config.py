from pathlib import Path

import yaml

from app.ui_config import public_ui_config

CONFIG_PATH = Path("config/portal.yaml")

with open(CONFIG_PATH, "r") as f:
    settings = yaml.safe_load(f)

# Reject invalid selections at startup, before serving either interface.
public_ui_config(settings)
