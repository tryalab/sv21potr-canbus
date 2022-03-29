#!python
import os.path
import sys
import sys
import json
from signal import signal
from textwrap import dedent
from turtle import clear
from urllib.parse import DefragResult


def get_json_txt(node, message):

    str = f"Input signals\n"

    # from file_handling import load_json, write_canbus_file
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

    # skapar en sträng str som sen används för att fylla påmed  de olika delarna
    # för att till slut användas för att skriva till fil. signals.txt
    str = f"Input signals\n"
    header = {'first': 'Name', 'Second': 'Type',
              'third': ' Description', 'fourth': 'Values'}
    str += dedent(f'''
    {header['first']:<31}| {header['Second']:<11}| {header['third']:<51}| {header['fourth']:<10}|
    {"":->110}
            ''')

    # loopa över "messages" så många gånger som det finns "id"
    for x in range(0, len(meddelande)):
        signals = json_data['messages'][x]['setter']
        texten = json_data['messages'][x]['signals']    # Här är "signalerna"
        if signals == node:                            # Här sätts vilken setter

            for signal in texten:
                if "range" in signal:
                    # error on :10 WHY??
                    str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}{signal['range']}\n"
                # Om Values innehåller någon av de som finns i "defines" i canbus.json så sätt in det som finns inom klamrarna
                if "values" in signal:
                    if signal['values'] == 'states':
                        # formatering se https://docs.python.org/3/tutorial/inputoutput.html
                        str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}{definitions['states']}\n"
                    if signal['values'] == 'vlwin':
                        str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}{definitions['vlwin']}\n"
                    if signal['values'] == 'system':
                        str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}{definitions['system']}\n"
                    if signal['values'] == 'status':
                        str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}{definitions['status']}\n"
                    if signal['values'] == 'esp32':
                        str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}{definitions['esp32']}\n"
    str += f"\n\nOutput signals\n"
    str += dedent(f'''
    {header['first']:<31}| {header['Second']:<11}| {header['third']:<51}| {header['fourth']:<10}|
    {"":->110}
            ''')
    for x in range(0, len(meddelande)):
        texten = json_data['messages'][x]['signals']    # Här är "signalerna"
        for utsignal in texten:
            if node in (utsignal.get("getters")):
                if "range" in utsignal:
                    str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {utsignal['range']}\n"
                if "values" in utsignal:
                    if utsignal['values'] == 'states':
                        str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {definitions['states']}\n"
                    if utsignal['values'] == 'vlwin':
                        str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {definitions['vlwin']}\n"
                    if utsignal['values'] == 'system':
                        str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {definitions['system']}\n"
                    if utsignal['values'] == 'status':
                        str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {definitions['status']}\n"
                    if utsignal['values'] == 'esp32':
                        str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {definitions['esp32']}\n"
    return str
