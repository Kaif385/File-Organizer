import os

def create_folder(path):
    os.makedirs(path, exist_ok=True)

def is_valid_folder(path):
    return os.path.exists(path) and os.path.isdir(path)