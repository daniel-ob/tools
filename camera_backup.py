#!/usr/bin/python3
"""Backup camera/mobile photos and videos. Copy only newly added files according to a CONFIG_FILE (JSON) like this one:

[{
    "origin": "/run/user/1000/gvfs/mtp:host=SAMSUNG_SAMSUNG_Android_XXXXXXXXXXXXXXXX/Phone/DCIM/Camera",
    "destination": "/home/user/Images/DCIM_Camera_bkp",
    "last_copied_file_mtime": 0
},
{
    "origin": "/run/user/1000/gvfs/mtp:host=SAMSUNG_SAMSUNG_Android_XXXXXXXXXXXXXXXX/Phone/WhatsApp/Media/WhatsApp Videos",
    "destination": "/home/user/Videos/WhatsApp_Videos_bkp",
    "last_copied_file_mtime": 1634474434.07039
}]

If last_copied_file_mtime is 0 or "" , then copy all files in origin.
Update "last_copied_file_mtime"s in CONFIG_FILE each time a new file is copied.
"""

import json
import os
import shutil
import sys
import time

CONFIG_FILE = os.path.expanduser("~/.camera_backup")

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
        # if last_copied_file_mtime not set, set to 0 so all files will be copied
        last_copied_file_mtime = folder["last_copied_file_mtime"] if folder["last_copied_file_mtime"] else 0
    except KeyError as key:
        sys.exit(f"key {key} not found in config file, folder {idx}")

    if not os.path.exists(origin):
        sys.exit(f"Origin \"{origin}\" not found. The device is connected?")

    print(f"Folder: {origin}")
    print(f"  last copied file modification time: {time.ctime(last_copied_file_mtime)}")

    # Create a list of all files (exclude directories) in origin
    files = []
    for filename in os.listdir(origin):
        file_abs_path = os.path.join(origin, filename)
        # Note that os.path.isfile needs absolute paths
        if os.path.isfile(file_abs_path):
            file = {}
            file["abs_path"] = file_abs_path
            file["mtime"] = os.path.getmtime(file_abs_path)
            files.append(file)

    # Sort files by modification time
    files.sort(key=lambda file: file["mtime"])

    new_file_found = False
    for file in files:
        if (file["mtime"] > last_copied_file_mtime):
            filename = os.path.basename(file["abs_path"])
            print(f"  copying {filename}")
            
            shutil.copy2(file["abs_path"], destination)
            new_file_found = True

    if new_file_found:
        # Update last copied file mtime
        config[idx]["last_copied_file_mtime"] = files[-1]["mtime"]
    else:
        print("  No new files found")

    print("-------")

# Update stored config file
with open(CONFIG_FILE, "w") as file:
    json.dump(config, file)
