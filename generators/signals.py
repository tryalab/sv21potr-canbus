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
    print(type(signals))
    """ for signal in signals:
        print(signal)
        #str += f"{signal['name']}      {signal['type']}          {signal['comment']}            \n"
 """
    """  str += "/**\n"
            if 'range' in signal:
                str += f"* @brief++++++++++ Function to set {signal['comment']} in range {signal['range']}\n"
            if 'values' in signal and signal['values'] == 'status':
                str += f"* @brief Function to set {signal['comment']} to either of these valid statuses [""ERROR"",""WARNING"",""OKAY""]\n"
            if 'values' in signal and signal['values'] == 'states':
                str += f"* @brief******** Function to set {signal['comment']} to either of these valid states [""ON"",""OFF""]\n"
                str += f"* @param value\n"
                str += "*\n"
                str += f"* @return true\n"
                str += f"* @return false\n"
                str += "*/\n"
                str += f"bool {stem}_set_{signal['name']}({signal['type']} value);\n"
                str += "\n" """

# print(str)
