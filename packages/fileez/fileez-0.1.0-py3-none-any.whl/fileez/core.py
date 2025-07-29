import os
import shutil
import json
import csv

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def read_lines(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.readlines()

def write(path, data, append=False):
    mode = 'a' if append else 'w'
    with open(path, mode, encoding='utf-8') as f:
        f.write(data)

def exists(path):
    return os.path.exists(path)

def delete(path):
    if os.path.isfile(path):
        os.remove(path)

def list_dir(path):
    return os.listdir(path)

def make_dir(path):
    os.makedirs(path, exist_ok=True)

def delete_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)

def copy_file(src, dst):
    shutil.copy2(src, dst)

def move_file(src, dst):
    shutil.move(src, dst)

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_csv(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        return list(reader)

def write_csv(path, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)