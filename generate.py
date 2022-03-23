import os
import sys
import json
import shutil
from pathlib import Path
from generators import service
from generators import common
from generators import canbus

ROOT = Path(__file__).parent

MODES = ["dev", "prod"]
NODES = ["com", "act", "sns", "hmi"]


# Load canbus.json
try:
    with open(Path(ROOT, 'canbus.json')) as file:
        try:
            data = json.load(file)
        except:
            print("Failed to read and parse the json file")
            exit(1)
except:
    print("Failed to open the json file")
    exit(1)


def print_arg_error():
    print("Error...")
    print("Usage: python generate.py -node {} -mode {}\n".format(NODES, MODES))
    exit(2)


# Get the user command

if len(sys.argv) == 5:
    if sys.argv[1] == '-node' and sys.argv[3] == '-mode':
        node = sys.argv[2].lower()
        mode = sys.argv[4].lower()
        if node not in NODES or mode not in MODES:
            print_arg_error()
    else:
        print_arg_error()
else:
    print_arg_error()


# Create directories and copy files in sources

ESP32_INCLUDE_DIR = None
TEENSY_INCLUDE_DIR = Path(ROOT.parent, 'include')
TEENSY_CANBUS_DIR = Path(ROOT.parent, 'lib', 'canbus')
if node == 'com':
    ESP32_INCLUDE_DIR = Path(ROOT.parent, 'esp32', 'include')
    TEENSY_INCLUDE_DIR = Path(ROOT.parent, 'teensy', 'include')
    TEENSY_CANBUS_DIR = Path(ROOT.parent, 'teensy', 'lib', 'canbus')

try:
    os.makedirs(TEENSY_INCLUDE_DIR, exist_ok=True)
    if ESP32_INCLUDE_DIR != None:
        os.makedirs(ESP32_INCLUDE_DIR, exist_ok=True)

    shutil.rmtree(TEENSY_CANBUS_DIR, True)
    os.makedirs(TEENSY_CANBUS_DIR)
    shutil.copytree(Path(ROOT, 'sources'),
                    TEENSY_CANBUS_DIR, dirs_exist_ok=True)
except:
    print("Failed to create directories and copy files")
    exit(3)


def write_file(file_name, content):
    try:
        with open(file_name, 'w') as file:
            file.write(content)
    except:
        print("Failed to write to {}".format(file_name))
        exit(4)


defines = data['defines']
del data['defines']

messages = []

for message in data['messages']:
    if message['setter'] == node:
        messages.append(message)
    else:
        for signal in message['signals']:
            if node in signal['getters']:
                messages.append(message)
                break
del data['messages']


for message in messages:
    for signal in message['signals']:
        if 'values' in signal:
            signal['values'] = defines[signal['values']]

write_file(Path(TEENSY_CANBUS_DIR, 'can_service.cpp'),
           service.get_content(node, mode, messages[:]))

write_file(Path(TEENSY_CANBUS_DIR, 'canbus.h'),
           canbus.get_canbus_header(node, mode, messages[:]))

write_file(Path(TEENSY_CANBUS_DIR, 'canbus.cpp'),
           canbus.get_canbus_source(node, mode, messages[:]))

write_file(Path(TEENSY_INCLUDE_DIR, 'common.h'),
           common.get_teensy_common_header(node, messages[:]))

if ESP32_INCLUDE_DIR != None:
    write_file(Path(ESP32_INCLUDE_DIR, 'common.h'),
               common.get_esp32_common_header(defines))
