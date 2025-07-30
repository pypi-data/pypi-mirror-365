import yaml
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).parent.parent.parent / "config.yaml"

def load_config(path=None):
    path = Path(path) if path else DEFAULT_CONFIG
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_config(config, path=None):
    path = Path(path) if path else DEFAULT_CONFIG
    with open(path, "w") as f:
        yaml.dump(config, f)
