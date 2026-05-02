from pathlib import Path
import json
import os

DATA_PATH = Path(os.getenv("DATA_PATH", "data.json"))

def load_data():
    if not (DATA_PATH).exists():
        return {}
    
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))

def save_data(data):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")