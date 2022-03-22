#!python
import os.path
import json
from signal import signal
from textwrap import dedent
from urllib.parse import DefragResult
# from file_handling import load_json, write_canbus_file


stem = "---: "


try:
    with open("canbus.json") as file:
        try:
            json_data = json.load(file)
        except:
            print("Failed to read and parse the json file")
            exit(1)
except:
    print("Failed to open the json file")
    exit(1)

for key, values in json_data.items():
    if key == 'nodes':
        noder = values

    if key == 'defines':
        text1 = values

    if key == 'messages':
        meddelande = values
print("noder is:", type(noder))
print("text1 is:", type(text1))
print("meddelande is:", type(meddelande))
print("lengd meddeande: ", len(meddelande), "\n")

str = f"Input signals\n"
str += dedent(f'''
Name          |     Type     |     Description    |     Values
--------------------------------------------------------------
        ''')

print(str)


for x in range(0, len(meddelande)):
    signals = json_data['messages'][x]['setter']  # change signals to setter
    texten = json_data['messages'][x]['signals']
    if signals == 'com':
        print("ACT lika med signals. X är lika med ", x)
        # print(texten)
        for signal in texten:
            str += f"{signal['name']}      {signal['type']}          {signal['comment']}            \n"
            print(str)
