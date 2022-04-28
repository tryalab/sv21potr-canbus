def get_text(name):
   text = f"void get_{name}_text(char *text, {name}_t {name});\n"
   return text

def get_text_function(name, insert_text, get_struct):
   text = \
f"""void get_{name}_text(char *text, {name}_t {name})
{{
    sprintf(text, "{name.capitalize()}({insert_text})", {get_struct});
}}
"""
   return text

def changed(name):
   text = f"bool is_{name}_changed({name}_t previous, {name}_t current);\n\n"
   return text

def struct(struct_member, struct_name):
   text = \
f"""
typedef struct {{
{struct_member}
}} {struct_name}_t;
"""
   return text

def inside_struct(struct_member, struct_name):
   text = \
f"""
    struct{{
{struct_member}
    }} {struct_name};
    """
   return text

def inside_inside_struct(struct_member, struct_name):
   text = \
f"""
        struct{{
{struct_member}\
        }} {struct_name};
        """
   return text

def canbus_get(struct, get_signal):
    return f"\t{struct} = canbus_get_{get_signal}();\n"

def canbus_is(struct, get_signal, key):
    if key == "enabled":
        if "state" in get_signal:
            get_signal = get_signal.replace(get_signal[len(get_signal) - 5:], "mode")
        else:
            get_signal = get_signal + "_mode"
    return f"\t{struct} = canbus_is_{get_signal}_{key}();\n"

def get_payloads_value(type_define, struct):
    return f'\tsprintf(payloads + strlen(payloads), "%{type_define}|", {struct});\n\n'

def get_payloads_status(struct):
    text =f"""\
    switch({struct})
    {{
    case UNINITIALIZED:
        sprintf(payloads + strlen(payloads), "%s|", "UNINITIALIZED");
        break;
    case OKAY:
        sprintf(payloads + strlen(payloads), "%s|", "OKAY");
        break;
    default:
        sprintf(payloads + strlen(payloads), "%s|", "ERROR");
        break;
    }}

"""
    return text

def get_payloads_status_system(struct):
    text = f"""\
    switch({struct})
    {{
    case WARNING:
        sprintf(payloads + strlen(payloads), "%s|", "WARNING");
        break;
    case OKAY:
        sprintf(payloads + strlen(payloads), "%s|", "OKAY");
        break;
    default:
        sprintf(payloads + strlen(payloads), "%s|", "ERROR");
        break;
    }}

"""
    return text

def get_string_functions():
    return """\
static const char *get_status_string(uint8_t status)
{
    char *status_text = "UNINITIALIZED";
    switch(status)
    {
        case OKAY:
            status_text = "OKAY";
            break;
        case ERROR:
            status_text = "ERROR";
            break;
        default:
            break;
    }
    return status_text;
}

static const char *get_system_string(uint8_t status)
{
    char *status_text = "WARNING";
    switch(status)
    {
        case OKAY:
            status_text = "OKAY";
            break;
        case ERROR:
            status_text = "ERROR";
            break;
        default:
            break;
    }
    return status_text;
}

static const char *get_esp32_string(uint8_t status)
{
    char *status_text = "UNINITIALIZED";
    switch(status)
    {
        case OKAY:
            status_text = "OKAY";
            break;
        case I2C_ERROR:
            status_text = "I2C_ERROR";
            break;
        case WIFI_ERROR:
            status_text = "WIFI_ERROR";
            break;
        case NTP_ERROR:
            status_text = "NTP_ERROR";
            break;
        case MQTT_ERROR:
            status_text = "MQTT_ERROR";
            break;
        default:
            break;
    }
    return status_text;
}"""

def get_functions_payloads_inserts(messages, struct, value, key, struct_text):
    get_functions = ""
    get_payloads = ""
    insert_inside = ""
    struct_texts = ""
    get_type, get_values = loop_through_json_get_type_values(messages, value, key)

    if get_type == "bool":
        get_functions += canbus_is(struct, value, key)
        get_payloads += get_payloads_is(struct)
        insert_inside += f"{key}: %s, "
        struct_texts += f'{struct_text} ? "TRUE" : "FALSE", '
    else:
        get_functions += canbus_get(struct, value)

        if get_values == ['UNINITIALIZED', 'OKAY', 'ERROR']:
            get_payloads += get_payloads_status(struct)
            insert_inside += f"{key}: %s, "
            struct_texts += f'get_status_string({struct_text}), '
        elif get_values == ['WARNING', 'OKAY', 'ERROR']:
            get_payloads += get_payloads_status_system(struct)
            insert_inside += f"{key}: %s, "
            struct_texts += f'get_system_string({struct_text}), '
        elif get_values == ['UNINITIALIZED', 'OKAY', 'I2C_ERROR', 'WIFI_ERROR', 'NTP_ERROR', 'MQTT_ERROR']:
            get_payloads += get_payloads_status_esp32(struct)
            insert_inside += f"{key}: %s, "
            struct_texts += f'get_esp32_string({struct_text}), '
        elif get_values == ['OFF', 'ON']:
            get_payloads += get_payloads_state(struct)
            insert_inside += f"{key}: %s, "
            struct_texts += f'{struct_text} == OFF ? "OFF" : "ON", '
        elif get_values == ['CLSD', 'OPNND']:
            get_payloads += get_payloads_vlvwin(struct)
            insert_inside += f"{key}: %s, "
            struct_texts += f'{struct_text} == CLSD ? "CLSD" : "OPNND", '
        else:
            struct_texts += f"{struct_text}, "
            if get_type == "float":
                typespec = "0.1f"
                insert_inside += f"{key}: %0.1f, "
            else:
                typespec = "u"
                if key == "possible" or key == "target":
                    insert_inside += f"{key}:[%u,%u] "
                elif key == "manual":
                    insert_inside += f"{key}["
                else:
                    if "rtc" not in value:
                        insert_inside += f"{key}: %u, "
            get_payloads += get_payloads_value(typespec, struct)

    return get_functions, get_payloads, insert_inside, struct_texts

def get_payloads_status_esp32(struct):
    text = f"""\
    switch({struct})
    {{
    case UNINITIALIZED:
        sprintf(payloads + strlen(payloads), "%s|", "UNINITIALIZED");
        break;
    case OKAY:
        sprintf(payloads + strlen(payloads), "%s|", "OKAY");
        break;
    case I2C_ERROR:
        sprintf(payloads + strlen(payloads), "%s|", "I2C_ERROR");
        break;
    case WIFI_ERROR:
        sprintf(payloads + strlen(payloads), "%s|", "WIFI_ERROR");
        break;
    case NTP_ERROR:
        sprintf(payloads + strlen(payloads), "%s|", "NTP_ERROR");
        break;
    default:
        sprintf(payloads + strlen(payloads), "%s|", "MQTT_ERROR");
        break;
    }}

"""
    return text

def get_payloads_state(struct):
    return f'\tsprintf(payloads + strlen(payloads), "%s|", {struct} == ON ? "ON" : "OFF");\n\n'

def get_payloads_vlvwin(struct):
    return f'\tsprintf(payloads + strlen(payloads), "%s|", {struct} == CLSD ? "CLSD" : "OPNND");\n\n'

def get_payloads_is(struct):
    return f'\tsprintf(payloads + strlen(payloads), "%s|", {struct} ? "TRUE" : "FALSE");\n\n'

def loop_through_json_get_type_values(messages, value, key):
    values = ""
    name_type = ""
    for message in messages:
        for signal in message['signals']:
            if key == "enabled" or key == "valid" or key == "updated":
                name_type = "bool"
                break
            elif signal.get("name") == value:
                name_type = signal.get("type")
                if "values" in signal:
                    values = signal["values"]
                break
    return name_type, values

def get_candata_header(nodes, messages):
    data_members = ""
    functions = ""
    node_members = ""
    signal_struct = ""
    signal_members = ""
    inside_struct_members=""
    insert_inside_struct_members =""
    node_struct = ""
    for node in nodes.values():
        name = node.get("name")
        data_members += f"\t{name}_t {name};\n"
        for key_signal, value_signal in node.items():
            if type(value_signal) is not dict:
                if key_signal != "name":
                    name_type, _ = loop_through_json_get_type_values(messages, value_signal, key_signal)
                    node_members += f"\t{name_type} {key_signal};\n"
            else:
                functions += get_text(key_signal)
                functions += changed(key_signal)
                node_members += f"\t{key_signal}_t {key_signal};\n"
                for key_inside_signal, value_inside_signal in value_signal.items():
                    if type(value_inside_signal) is not dict:
                        name_type, _ = loop_through_json_get_type_values(messages, value_inside_signal, key_inside_signal)
                        signal_members += f"\t{name_type} {key_inside_signal};\n"
                    else:
                        for min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                name_type, _ = loop_through_json_get_type_values(messages, value_min_max, min_max)
                                inside_struct_members += f"\t\t{name_type} {min_max};\n"
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        name_type, _ = loop_through_json_get_type_values(messages, value_inside_min_max, key_inside_min_max)
                                        insert_inside_struct_members += f"\t\t\t{name_type} {key_inside_min_max};\n"
                                insert_inside_struct = inside_inside_struct(insert_inside_struct_members, min_max)
                                insert_inside_struct_members =""
                                inside_struct_members += f"{insert_inside_struct}"
                        signal_members += inside_struct(inside_struct_members[:-1], key_inside_signal)
                        inside_struct_members = ''
                signal_struct += struct(signal_members[:-1], key_signal)
                signal_members = ""
        node_struct += struct(node_members[:-1], name)
        node_members =""
        

    data_struct = struct(data_members[:-1], "data")
    text_struct =f"""\
#ifndef CANDATA_H
#define CANDATA_H

#include <stdint.h>
#define PAYLOADS_LENGTH (768U)

    {signal_struct}
    {node_struct}
    {data_struct}
    
data_t get_candata(void);

void get_payloads(char *payloads);

{functions[:-2]}

#endif /* CANDATA_H */    
    """
    return text_struct

def get_candata_source(nodes, messages):

    get_functions = ""
    payloads_functions = ""
    text_function = ""
    insert_inside = ""
    struct_text =""
    insert_struct_text = ""

    for node in nodes.values():
        name = node.get("name")
        for key_signal, value_signal in node.items():
            if type(value_signal) is not dict:
                if key_signal != "name":
                    struct = f"data.{name}.{key_signal}"
                    get_function, payloads_function, _, _ = get_functions_payloads_inserts(messages, struct, value_signal, key_signal, struct_text)
                    get_functions += get_function
                    payloads_functions += payloads_function
            else:
                for key_inside_signal, value_inside_signal in value_signal.items():
                    
                    _, _, insert, _ = get_functions_payloads_inserts(messages, struct, value_inside_signal, key_inside_signal, struct_text)
                    if type(value_inside_signal) is not dict:
                        struct = f"data.{name}.{key_signal}.{key_inside_signal}"
                        struct_text = f"{key_signal}.{key_inside_signal}"
                        get_function, payloads_function, insert, struct_texts = get_functions_payloads_inserts(messages, struct, value_inside_signal, key_inside_signal, struct_text)
                        insert_struct_text += struct_texts
                        insert_inside += insert
                        get_functions += get_function
                        payloads_functions += payloads_function
                    else:
                        
                        _, _, insert, _ = get_functions_payloads_inserts(messages, struct, value_inside_signal, key_inside_signal, struct_text)
                        insert_inside += insert
                        for key_min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                struct = f"data.{name}.{key_signal}.{key_inside_signal}.{key_min_max}"
                                struct_text = f"{key_signal}.{key_inside_signal}.{key_min_max}"
                                get_function, payloads_function, insert, struct_texts = get_functions_payloads_inserts(messages, struct, value_min_max, key_min_max, struct_text)
                                insert_struct_text += struct_texts
                                insert_inside += insert
                                get_functions += get_function
                                payloads_functions += payloads_function
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        if key_inside_min_max == "value":
                                            struct_text = f"{key_signal}.{key_inside_signal}.{key_min_max}.{key_inside_min_max}"
                                        else:
                                            struct_text = ""
                                        struct = f"data.{name}.{key_signal}.{key_inside_signal}.{key_min_max}.{key_inside_min_max}"
                                        get_function, payloads_function, _, struct_texts = get_functions_payloads_inserts(messages, struct, value_inside_min_max, key_inside_min_max, struct_text)
                                        if key_inside_min_max == "value":
                                            insert_struct_text += struct_texts
                                        get_functions += get_function
                                        payloads_functions += payloads_function
                start = len(insert_inside) - 2
                stop = start + 2
                if key_inside_signal == 'manual' or key_inside_signal == 'target':
                    insert_inside = insert_inside[0:start:] + insert_inside[stop::] + "]"
                else:
                    insert_inside = insert_inside[0:start:] + insert_inside[stop::]

                start = len(insert_struct_text) - 2
                stop = start + 2
                insert_struct_text = insert_struct_text[0:start:] + insert_struct_text[stop::]
                text_function += get_text_function(key_signal, insert_inside, insert_struct_text)

                insert_inside = ""
                insert_struct_text = ""
    text = \
f"""                         
#include <stdio.h>         
#include <string.h>
#include "common.h"
#include "canbus.h"
#include "candata.h"

{get_string_functions()}

data_t get_candata(void)
{{
\tdata_t data;

{get_functions[:-1]}
\treturn data;
}}

void get_payloads(char *payloads)
{{
\tdata_t data = get_candata();

{payloads_functions}\
}}
{text_function}
"""
    return text
