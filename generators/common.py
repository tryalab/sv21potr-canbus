def get_teensy_common_header(node, messages):
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
