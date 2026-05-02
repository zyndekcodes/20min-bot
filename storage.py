from pathlib import Path
import json
import os

DATA_PATH = Path(os.getenv("DATA_PATH", "/data.json"))

def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=4), encoding="utf-8")