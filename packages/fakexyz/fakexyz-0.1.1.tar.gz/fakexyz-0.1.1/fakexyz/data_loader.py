import os
import json

def load_data():
    data = {}
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "data")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            country_code = filename.split(".")[0]
            file_path = os.path.join(data_dir, filename)
            with open(file_path, encoding="utf-8") as f:
                data[country_code] = json.load(f)
    return data
