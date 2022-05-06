from textwrap import dedent


def get_json_txt(node, messages):
    # skapar en sträng str som sen används för att fylla påmed  de olika delarna
    # för att till slut användas för att skriva till fil. signals.txt

    str = f"Output signals\n"
    header = {'first': 'Name', 'Second': 'Type',
              'third': ' Description', 'fourth': 'Values'}
    str += dedent(f'''
    {header['first']:<31}| {header['Second']:<11}| {header['third']:<51}| {header['fourth']:<10}
    {"":->110}
            ''')

    # loopa över "messages" så många gånger som det finns "id"
    for message in messages:
        if message['setter'] == node:
            for signal in message['signals']:
                if "range" in signal:
                    str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}| {signal['range']}\n"
                else:
                    str += f"{signal['name']:<31}| {signal['type']:<11}| {signal['comment']:<51}| {signal['values']}\n"

    str += f"\n\nInput signals\n"
    str += dedent(f'''
    {header['first']:<31}| {header['Second']:<11}| {header['third']:<51}| {header['fourth']:<10}
    {"":->110}
            ''')
    for message in messages:
        for utsignal in message['signals']:
            if node in utsignal['getters']:
                if "range" in utsignal:
                    str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {utsignal['range']}\n"
                else:
                    str += f"{utsignal['name']:<31}| {utsignal['type']:<11}| {utsignal['comment']:<51}| {utsignal['values']}\n"
    return str
