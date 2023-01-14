#!/usr/bin/python3
"""Backup phone files. Copy newly added and modified files according to CONFIG_FILE (JSON) like this:
[{
    "origin": "/run/user/1000/gvfs/mtp:host=SAMSUNG_SAMSUNG_Android_XX/Phone/DCIM/Camera",
    "destination": "/home/user/PhoneBKP/Camera",
},
{
    "origin": "/run/user/1000/gvfs/mtp:host=SAMSUNG_SAMSUNG_Android_XX/Phone/Documents",
    "destination": "/home/user/PhoneBKP/Documents",
}]
"""

import json
import os
from pathlib import Path
import shutil
import sys
import time

CONFIG_FILE = os.path.expanduser("~/.phone_backup")

# Read config file (JSON)
try:
    with open(CONFIG_FILE) as file:
        config = json.load(file)
except FileNotFoundError:
    sys.exit(f"Config file not found: {CONFIG_FILE}")
except json.JSONDecodeError as e:
    sys.exit(f"Please verify config file ({CONFIG_FILE}) JSON syntax: {e}")

for idx, folder in enumerate(config):
    try:
        origin = folder["origin"]
        destination = folder["destination"]
    except KeyError as key:
        sys.exit(f"key {key} not found in config file, folder {idx}")

    if not os.path.exists(origin):
        sys.exit(f"Origin \"{origin}\" not found. Is the device connected?")

    # Find mtime of last destination file
    destination_files = [item for item in Path(destination).iterdir() if item.is_file()]
    destination_last_file = max(destination_files, key=lambda f: f.stat().st_mtime, default=None)
    destination_last_file_mtime = destination_last_file.stat().st_mtime or 0

    print(f"Folder: {origin}")
    print(f"  last copied file modification time: {time.ctime(destination_last_file_mtime)}")

    # Copy newly added files
    origin_files = [item for item in Path(origin).iterdir() if item.is_file()]
    origin_files.sort(key=lambda f: f.stat().st_mtime)
    new_file_found = False
    for file in origin_files:
        if file.stat().st_mtime > destination_last_file_mtime:
            print(f"  copying {file.name}")
            shutil.copy2(file, destination)
            new_file_found = True

    if not new_file_found:
        print("  No new files found")

    print("-------")
