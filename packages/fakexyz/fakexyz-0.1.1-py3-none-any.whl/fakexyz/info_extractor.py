import random
from .data_loader import load_data

_data = load_data()

def get_country_info():
    return _data["meta"]

def get_personal_profile():
    return _data["profile"]

def get_random_address():
    return random.choice(_data["addresses"])
