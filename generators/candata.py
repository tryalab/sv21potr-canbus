def get_text(name):
   text = f"void get_{name}_text(char *text, {name}_t {name});\n"
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
   text = f"""\
    struct{{
        {struct_member}
        }} {struct_name};
    """
   return text

def canbus_get(struct, get_signal):
    return f"\t{struct} = canbus_get_{get_signal}();\n"

def get_payloads_value(type_define, struct):
    return f'\tsprintf(payloads + strlen(payloads), "%{type_define}|", {struct});\n'

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

def get_candata_header(nodes):
    text = ""
    data_members = ""
    functions = ""
    node_members = ""
    signal_struct = ""
    signal_members = ""
    inside_struct_members=""
    node_struct = ""
    for node in nodes.values():
        name = node.get("name")
        data_members += f"\t{name}_t {name};\n"
        for key_signal, value_signal in node.items():
            if type(value_signal) is not dict:
                if key_signal != "name":
                    node_members += f"\tuint8_t {key_signal};\n"
            else:
                functions += get_text(key_signal)
                functions += changed(key_signal)
                node_members += f"\t{key_signal}_t {key_signal};\n"
                for key_inside_signal, value_inside_signal in value_signal.items():
                    if type(value_inside_signal) is not dict:
                        if value_inside_signal == "temperature":
                            signal_members += f"\tfloat {key_inside_signal};\n"
                        elif value_inside_signal == "flow_rate":
                            signal_members += f"\tuint16_t {key_inside_signal};\n"
                        else:
                            signal_members += f"\tuint8_t {key_inside_signal};\n"
                    else:
                        for min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                inside_struct_members += f"\tuint8_t {min_max};\n"
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        if value_inside_min_max == "water_consumed_target_max":
                                            insert_inside_struct = inside_inside_struct(f"\tuint16_t {key_inside_min_max};", min_max)
                                        else:
                                            insert_inside_struct = inside_inside_struct(f"\tuint8_t {key_inside_min_max};", min_max)
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

    {data_struct}
    {node_struct}
    {signal_struct}
data_t get_candata(void);

void get_payloads(char *payloads);

{functions[:-2]}

#endif /* CANDATA_H */    
    """
    return text_struct

def get_candata_source(nodes):

    get_functions = ""
    payloads_functions = ""

    for node in nodes.values():
        name = node.get("name")
        for key_signal, value_signal in node.items():
            if type(value_signal) is not dict:
                if key_signal != "name":
                    get_functions += canbus_get(f"data.{name}.{key_signal}", value_signal)
                    if key_signal == "status":
                        payloads_functions += get_payloads_status(f"data.{name}.{key_signal}")
                    elif key_signal == "state":
                        payloads_functions += get_payloads_state(f"data.{name}.{key_signal}")
                    else:
                        if value_signal == "temperature":
                            payloads_functions += get_payloads_value("0.1f C", f"data.{name}.{key_signal}")
                        else:
                            payloads_functions += get_payloads_value("u", f"data.{name}.{key_signal}")
            else:   
                for key_inside_signal, value_inside_signal in value_signal.items():
                    if type(value_inside_signal) is not dict:
                        get_functions += canbus_get(f"data.{name}.{key_signal}.{key_inside_signal}", value_inside_signal)
                        if key_inside_signal == "status":
                            payloads_functions += get_payloads_status(f"data.{name}.{key_signal}.{key_inside_signal}")
                        elif key_inside_signal == "state":
                            payloads_functions += get_payloads_state(f"data.{name}.{key_signal}.{key_inside_signal}")
                        else:
                            if value_inside_signal == "temperature":
                                payloads_functions += get_payloads_value("0.1f C", f"data.{name}.{key_signal}.{key_inside_signal}")
                            else:
                                payloads_functions += get_payloads_value("u", f"data.{name}.{key_signal}.{key_inside_signal}")
                    else:
                        for min_max, value_min_max in value_inside_signal.items():
                            if type(value_min_max) is not dict:
                                get_functions += canbus_get(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}", value_min_max)
                                if min_max == "status":
                                    payloads_functions += get_payloads_status(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                                elif min_max == "state":
                                    payloads_functions += get_payloads_state(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                                else:
                                    if value_min_max == "temperature":
                                        payloads_functions += get_payloads_value("0.1f C", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                                    else:
                                        payloads_functions += get_payloads_value("u", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}")
                            else:
                                for key_inside_min_max, value_inside_min_max in value_min_max.items():
                                    if type(value_inside_min_max) is not dict:
                                        get_functions += canbus_get(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}", value_inside_min_max)
                                        if key_inside_min_max == "status":
                                            payloads_functions += get_payloads_status(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
                                        elif key_inside_min_max == "state":
                                            payloads_functions += get_payloads_state(f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
                                        else:
                                            if value_inside_min_max == "temperature":
                                                payloads_functions += get_payloads_value("0.1f C", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
                                            else:
                                                payloads_functions += get_payloads_value("u", f"data.{name}.{key_signal}.{key_inside_signal}.{min_max}.{key_inside_min_max}")
    text = \
f"""                         
#include <stdio.h>         
#include <string.h>
#include "common.h"
#include "canbus.h"
#include "candata.h"
data_t data;

data_t get_candata(void)
{{
{get_functions[:-1]} 
}}

void get_payloads(char *payloads)
{{
\tdata_t data = get_candata();
{payloads_functions}
}}
"""
    return text
