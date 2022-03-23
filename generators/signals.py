#!python
import os.path
import sys
import sys
import json
from signal import signal
from textwrap import dedent
from urllib.parse import DefragResult
# from file_handling import load_json, write_canbus_file

# cmd_line_argument =


# Open canbus.json för att läsa den och hantera eventuella fel vid öppnandet/läsandet.
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


# Tar ut tre olika delar, för att kunna fortsätta bearbeta dem separat
for key, values in json_data.items():
    if key == 'nodes':
        noder = values

    if key == 'defines':
        definitions = values

    if key == 'messages':
        meddelande = values

# Utskrifter under utvecklandet av koden för att hålla koll på saker
#
print("noder is:", type(noder))
print("definitions is:", type(definitions))
print(definitions)
print("meddelande is:", type(meddelande))
print("lengd meddeande: ", len(meddelande), "\n")


# skapar en sträng str som sen används för att fylla påmed  de olika delarna
# för att till slut användas för att skriva till fil. signals.txt
str = f"Input signals\n"
header = {'first': 'Name', 'Second': 'Type',
          'third': ' Description', 'fourth': 'Values'}
str += dedent(f'''
{header['first']:<20}|{header['Second']:<10}|{header['third']:<41}|{header['fourth']:<10}|
{"":->90}
        ''')

# Ännu en koll av resultatet på väg
print(str)

# loopa över "messages" så många gånger som det finns "id"
for x in range(0, len(meddelande)):
    signals = json_data['messages'][x]['setter']
    texten = json_data['messages'][x]['signals']  # Här är "signalerna"
    if signals == 'com':
        print("ACT lika med signals. X är lika med ", x)
        # print(texten)
        for signal in texten:
            if "range" in signal:
                # error on :10 WHY??
                str += f"{signal['name']:<21}{signal['type']:<11}{signal['comment']:<41}{signal['range']}\n"
            # Om Values innehåller någon av de som finns i "defines" i canbus.json så sätt in det som finns inom klamrarna
            if "values" in signal:
                if signal['values'] == 'states':
                    str += f"{signal['name']:<21}{signal['type']:<11}{signal['comment']:<41}{definitions['states']}\n"
                if signal['values'] == 'vlwin':
                    str += f"{signal['name']:<21}{signal['type']:<11}{signal['comment']:<41}{definitions['vlwin']}\n"
                if signal['values'] == 'system':
                    str += f"{signal['name']:<21}{signal['type']:<11}{signal['comment']:<41}{definitions['system']}\n"
                if signal['values'] == 'status':
                    str += f"{signal['name']:<21}{signal['type']:<11}{signal['comment']:<41}{definitions['status']}\n"
                if signal['values'] == 'esp32':
                    str += f"{signal['name']:<21}{signal['type']:<11}{signal['comment']:<41}{definitions['esp32']}\n"
                #str += f"{signal['name']:<21}{signal['type']:<11}{signal['comment']:<41}{signal['values']}\n"

print(str)
