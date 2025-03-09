import json
import os

def save_progress(filename, page, data):
    with open(filename, "a") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
    with open(filename + ".progress", "a") as f:
        f.write(str(page) + "\n")
    print(f"Saved progress for page {page}, Total Entries: {len(data)}")

def load_progress(filename):
    progress_file = filename + ".progress"
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            return set(int(line.strip()) for line in f)
    return set()
