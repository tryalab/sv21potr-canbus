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

def get_payloads_state(struct):
    text = f"""\
    if ({struct} == ON)
    {{
        sprintf(payloads + strlen(payloads), "%s|", "ON");
    }}
    else
    {{
        sprintf(payloads + strlen(payloads), "%s|", "OFF");
    }}
    
"""
    return text

def loop_through_json_get_type(messages, signal_name, key):
    for message in messages:
        for signal in message['signals']:
            if key == "enabled" or key == "valid" or key == "updated":
                name_type = "bool"
                break
            elif signal.get("name") == signal_name:
                name_type = signal.get("type")
                break
    return name_type

def loop_through_json_check(messages, name):
    for message in messages:
        for signal in message['signals']:
            if signal.get("name") in signal:
                name_type = signal.get("type")
                break
    return name_type
    
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
                    name_type = loop_through_json_get_type(messages, value_signal, key_signal)
                    node_members += f"\t{name_type} {key_signal};\n"
            else:
                functions += get_text(key_signal)
                functions += changed(key_signal)
                node_members += f"\t{key_signal}_t {key_signal};\n"
                for key_inside_signal, value_inside_signal in value_signal.items():
                    if type(value_inside_signal) is not dict:
                        name_type = loop_through_json_get_type(messages, value_inside_signal, key_inside_signal)
                        signal_members += f"\t{name_type} {key_inside_signal};\n"
                    else:
                        for min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                name_type = loop_through_json_get_type(messages, value_min_max, min_max)
                                inside_struct_members += f"\t\t{name_type} {min_max};\n"
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        name_type = loop_through_json_get_type(messages, value_inside_min_max, key_inside_min_max)
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
#define PAYLOAD_LENGTH (768U)

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
    payloads_functions_value = ""
    payloads_functions_state = ""
    payloads_functions_status = ""
    text_function = ""
    insert_key_inside = ""
    struct_text =""

    for node in nodes.values():
        name = node.get("name")
        for key_signal, value_signal in node.items():
            if type(value_signal) is not dict:
                if key_signal != "name":
                    get_functions += canbus_get(f"data.{name}.{key_signal}", value_signal)
                    if key_signal == "status":
                        payloads_functions_status += get_payloads_status(f"data.{name}.{key_signal}")
                    elif key_signal == "state":
                        payloads_functions_state += get_payloads_state(f"data.{name}.{key_signal}")
                    else:
                        if value_signal == "temperature":
                            payloads_functions_value += get_payloads_value("0.1f", f"data.{name}.{key_signal}")
                        else:
                            payloads_functions_value += get_payloads_value("u", f"data.{name}.{key_signal}")
            else:   
                for key_inside_signal, value_inside_signal in value_signal.items():
                    if type(value_inside_signal) is not dict:
                        struct = f"data.{name}.{key_signal}.{key_inside_signal}"
                        struct_text += f"{key_signal}.{key_inside_signal}, "
                        insert_key_inside += f"{key_inside_signal}: %d, "
                        get_functions += canbus_get(struct, value_inside_signal)
                        if key_inside_signal == "status":
                            payloads_functions_status += get_payloads_status(struct)
                        elif key_inside_signal == "state":
                            payloads_functions_state += get_payloads_state(struct)
                        else:
                            if value_inside_signal == "temperature":
                                payloads_functions_value += get_payloads_value("0.1f", struct)
                            else:
                                payloads_functions_value += get_payloads_value("u", struct)
                        
                    else:
                        insert_key_inside += f"{key_inside_signal}: %d, "
                        for min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                struct_text += f"{key_signal}.{key_inside_signal}.{min_max}, "
                                if min_max == "updated" or min_max == "valid" or min_max == "enabled":
                                    get_functions += canbus_is(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}", value_min_max, min_max)
                                else:    
                                    get_functions += canbus_get(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}", value_min_max)
                                if min_max == "status":
                                    payloads_functions_status += get_payloads_status(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                                elif min_max == "state":
                                    payloads_functions_state += get_payloads_state(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                                else:
                                    if value_min_max == "temperature":
                                        payloads_functions_value += get_payloads_value(
                                            "0.1f", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                                    else:
                                        payloads_functions_value += get_payloads_value("u", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        if key_inside_min_max == "updated" or key_inside_min_max == "valid" or key_inside_min_max == "enabled":
                                            get_functions += canbus_is(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}", value_inside_min_max, key_inside_min_max)
                                        else:
                                            get_functions += canbus_get(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}", value_inside_min_max)
                                        if key_inside_min_max == "status":
                                            payloads_functions_status += get_payloads_status(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
                                        elif key_inside_min_max == "state":
                                            payloads_functions_state += get_payloads_state(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
                                        else:
                                            if value_inside_min_max == "temperature":
                                                payloads_functions_value += get_payloads_value("0.1f C", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
                                            else:
                                                payloads_functions_value += get_payloads_value("u", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
                start = len(insert_key_inside) - 2
                stop = start + 2
                insert_key_inside = insert_key_inside[0:start:] + insert_key_inside[stop::]
                start = len(struct_text) - 2
                stop = start + 2
                struct_text = struct_text[0:start:] + struct_text[stop::]
                text_function += get_text_function(key_signal, insert_key_inside, struct_text)
                insert_key_inside = ""
                struct_text = ""
    text = \
f"""                         
#include <stdio.h>         
#include <string.h>
#include "common.h"
#include "canbus.h"
#include "candata.h"

data_t get_candata(void)
{{
\tdata_t data;

{get_functions[:-1]}
\treturn data;
}}

void get_payloads(char *payloads)
{{
\tdata_t data = get_candata();

{payloads_functions_status}
{payloads_functions_state}
{payloads_functions_value}\
}}
{text_function}
"""
    return text
