import os
import json

BASE_DIR =os.path.dirname(os.path.abspath(__file__))
MEMORY_PATH = os.path.join(BASE_DIR, "memory.json")

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

    return []

def save_memory(messages):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
         json.dump(messages, f, indent=2, ensure_ascii=False)