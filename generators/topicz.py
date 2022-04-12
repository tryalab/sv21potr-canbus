def get_topics(messages):
    text = ""

    for message in messages:
        setter = message.get("setter")
        for signal in message["signals"]:
            name = signal.get("name")
            text += f'"/{setter}/{name}",\n'
    text 
    return text