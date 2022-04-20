def get_topics(nodes):
    text = ""
    length_count = 0
    total_count = 0
    for node in nodes.values():
        name = node.get("name") 
        for key_signal, value_signal in node.items():
            if type(value_signal) is not dict:
                if key_signal != "name":
                    topic = f'"/{name}/{key_signal}"'
                    if len(topic) > length_count:
                        length_count = len(topic)
                    text += f'\t{topic},\n'
                    total_count += 1
            else:
                for key_inside_signal, value_inside_signal in value_signal.items():
                    if type(value_inside_signal) is not dict:
                        topic = f'"/{name}/{key_signal}/{key_inside_signal}"'
                        if len(topic) > length_count:
                            length_count = len(topic)
                        text += f'\t{topic},\n'
                        total_count += 1
                    else:
                        for min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                topic = f'"/{name}/{key_signal}/{key_inside_signal}/{min_max}"'
                                if len(topic) > length_count:
                                    length_count = len(topic)
                                text += f'\t{topic},\n'
                                total_count += 1
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        topic = f'"/{name}/{key_signal}/{key_inside_signal}/{min_max}/{key_inside_min_max}"'
                                        if len(topic) > length_count:
                                            length_count = len(topic)
                                        text += f'\t{topic},\n'
                                        total_count += 1

    text_total = f"""\
#define TOPICS_LENGTH {length_count}
#define TOPICS_TOTAL {total_count}

char topics[TOPICS_TOTAL][TOPICS_LENGTH] ={{
{text[:-2]}}};
"""
    return text_total

def get_teensy_common_header(node, nodes, messages):
    macros = ''
    values = []
    name_list = []

    if node == "sns":
        macros += "#define ADC_RESOLUTION 10\n"

    for message in messages:
        for signal in message['signals']:
            if message['setter'] == node or node in signal['getters']:
                if 'values' in signal:
                    if signal['values'] not in values:
                        values.append(signal['values'])
                        for value in values:
                            for index, name in enumerate(value):
                                if name not in name_list:
                                    name_list.append(name)
                                    macros += f"#define {name} {index}\n"
    
    if node == "com":
        macros += get_topics(nodes)

    header_content = f"""\
#ifndef COMMON_H
#define COMMON_H
   
{macros}
#endif /* COMMON_H */"""

    return header_content


def get_esp32_common_header(defines):
    macros = ''
    for index, name in enumerate(defines.get('esp32')):
        macros += f"#define {name} {index}\n"

    header_esp32 = f"""\
#ifndef COMMON_H
#define COMMON_H
    
{macros}
#endif /* COMMON_H */"""

    return header_esp32
