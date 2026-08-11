import json
from datetime import datetime

from paths import base_dir

STATE_PATH = base_dir() / "last_run.json"


def load_last_run():
    if not STATE_PATH.exists():
        return None
    with open(STATE_PATH) as f:
        data = json.load(f)
    return datetime.fromisoformat(data["last_run"])


def save_last_run(when):
    with open(STATE_PATH, "w") as f:
        json.dump({"last_run": when.isoformat()}, f)
