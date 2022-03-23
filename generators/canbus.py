
def set_test_double_function(name, type, valid, if_float_multiply, index, start, length):
    text = \
        f"""
bool canbus_test_set_{name}({type} value)
{{
    bool status = false;

    if ({valid})
    {{\
        {if_float_multiply}
        can_signal_write({index}, {start}, {length}, value);
        status = true;
    }}

    return status;
}}
              """
    return text


def set_function(name, type, valid, if_float_multiply, index, start, length):
    text = \
        f"""
bool canbus_set_{name}({type} value)
{{
    bool status = false;

    if ({valid})
    {{\
        {if_float_multiply}
        can_signal_write({index}, {start}, {length}, value);
        status = true;
    }}

    return status;
}}
              """
    return text


def get_test_double_function(name, type, if_float_devide, index, start, length):
    text = \
        f"""
{type} canbus_test_get_{name}(void)
{{
    {type} value = 0;
    value = ({type})can_signal_read({index}, {start}, {length});\
    {if_float_devide}
    return value;
}}
              """
    return text


def get_function(name, type, if_float_devide, index, start, length):
    text = \
        f"""
{type} canbus_get_{name}(void)
{{
    {type} value = 0;
    value = ({type})can_signal_read({index}, {start}, {length});\
    {if_float_devide}
    return value;
}}
              """
    return text


def update_function(name, type, get_update):
    text = \
        f"""
bool canbus_is_{name}_updated(void)
{{
    bool status = false;
    {type} previous_value = 0;

    if(previous_value != {get_update})
    {{
        previous_value = {get_update};
        status = true;
    }}

    return status;
}}
              """
    return text


def control_function(name):
    text = \
        f"""
bool canbus_is_{name}_enabled(void)
{{

}}
              """
    return text


def calibration_function(name, type, set_valid):
    text = \
        f"""
bool canbus_is_{name}_valid({type} value)
{{
    return {set_valid};
}}
              """
    return text


def get_canbus_source(node, mode, messages):
    get = ''
    set = ''
    control_bit = ''

    for index, message in enumerate(messages):
        for signal in message["signals"]:
            if message['setter'] == node or node in signal['getters']:
                if "range" in signal:
                    low_boundary = str(signal["range"][0])
                    high_boundary = str(signal["range"][-1])
                elif "values" in signal:
                    high_boundary = signal["values"][-1]
                if signal.get("type") == "float":
                    if_float_multiply = '''\n\t\tvalue *= 10;'''
                    if_float_devide = "\n\tvalue /= 10;"
                else:
                    if_float_multiply = ""
                    if_float_devide = ""

                valid = ''
                if 'range' in signal:
                    if signal["range"][0] != 0:
                        valid = f"""{low_boundary} <= value && value <= {high_boundary}"""
                    else:
                        valid = f"""value <= {high_boundary}"""
                else:
                    valid = f"""value <= {high_boundary}"""

                if message['setter'] == node and node in signal['getters']:

                    set += set_function(signal.get("name"), signal.get("type"), valid,
                                        if_float_multiply, index, signal.get("start"), signal.get("length"))

                    get += get_function(signal.get("name"), signal.get("type"),
                                        if_float_devide, index, signal.get("start"), signal.get("length"))

                elif message['setter'] == node and node not in signal['getters']:
                    set += set_function(signal.get("name"), signal.get("type"), valid,
                                        if_float_multiply, index, signal.get("start"), signal.get("length"))

                    if mode == 'dev':
                        get += get_test_double_function(
                            signal.get("name"), signal.get("type"), if_float_devide, index, signal.get("start"), signal.get("length"))

                elif message['setter'] != node and node in signal['getters']:
                    get += get_function(signal.get("name"), signal.get("type"),
                                        if_float_devide, index, signal.get("start"), signal.get("length"))

                    if mode == 'dev':
                        set += set_test_double_function(signal.get("name"), signal.get(
                            "type"), valid, if_float_multiply, index, signal.get("start"), signal.get("length"))

                if node in signal['getters']:
                    if 'update' in signal:
                        get_update = f"""canbus_get_{signal.get("name")}()"""
                        control_bit += update_function(
                            signal.get("name"), signal.get("type"), get_update)

                    elif 'control' in signal:
                        control_bit += control_function(
                            signal.get("name"))

                    elif 'calibration' in signal:
                        if mode == 'dev':
                            set_valid = f"""canbus_test_set_{signal.get("name")}(value)"""
                        elif mode == 'prod':
                            set_valid = f"""canbus_set_{signal.get("name")}(value)"""

                        control_bit += calibration_function(
                            signal.get("name"), signal.get("type"), set_valid)

    text = f'''\
# include "canbus.h"
# include "can_signal.h"
# include "common.h"

{set}
{get}
{control_bit}\
'''
    return text


def set_test_double_header(comment, name, type):
    text = \
        f"""
/**
 * @brief This function is used as test double to set {comment}.
 * @param value The value to set.
 * @return true if value is valid otherwise return false.
 */
bool canbus_test_set_{name}({type} value);
              """
    return text


def set_header(comment, name, type):
    text = \
        f"""
/**
 * @brief This function is used to set {comment}.
 * @param value The value to set.
 * @return true if value is valid otherwise return false.
 */
bool canbus_set_{name}({type} value);
              """
    return text


def get_test_double_header(comment, name, type):
    text = \
        f"""
/**
 * @brief This function is used as test double to get {comment}.
 * @return {name} The extracted data.
 */
{type} canbus_test_get_{name}(void);
              """
    return text


def get_header(comment, name, type):
    text = \
        f"""
/**
 * @brief This function is used to get {comment}.
 * @return {type} The extracted data.
 */
{type} canbus_get_{name}(void);
              """
    return text


def update_header(comment, name):
    text = \
        f"""
/**
 * @brief This function is used to check if {comment} is updated.
 * @return true if signal is updated.
 */
bool canbus_is_{name}_updated(void);
              """
    return text


def control_header(comment, name):
    text = \
        f"""
/**
 * @brief This function is used to check if {comment} is enabled.
 * @return true if signal is enabled.
 */
bool canbus_is_{name}_enabled(void);
              """
    return text


def calibration_header(comment, name):
    text = \
        f"""
/**
 * @brief This function is used to check if {comment} is valid.
 * @return true if value in range is valid.
 */
bool canbus_is_{name}_valid(void);
              """
    return text


def get_canbus_header(node, mode, messages):
    text = ''
    control_bit = ''
    set = ''
    get = ''

    for message in messages:
        for signal in message["signals"]:
            if message['setter'] == node or node in signal['getters']:

                if message['setter'] == node and node in signal['getters']:
                    set += set_header(signal.get(
                        "comment"), signal.get("name"), signal.get("type"))
                    get += get_header(signal.get(
                        "comment"), signal.get("name"), signal.get("type"))

                elif message['setter'] == node and node not in signal['getters']:
                    set += set_header(signal.get(
                        "comment"), signal.get("name"), signal.get("type"))

                    if mode == 'dev':
                        get += get_test_double_header(signal.get(
                            "comment"), signal.get("name"), signal.get("type"))

                elif message['setter'] != node and node in signal['getters']:
                    get += get_header(signal.get(
                        "comment"), signal.get("name"), signal.get("type"))

                    if mode == 'dev':
                        set += set_test_double_header(signal.get(
                            "comment"), signal.get("name"), signal.get("type"))

                if node in signal['getters']:
                    if 'update' in signal:
                        control_bit += update_header(
                            signal.get("comment"), signal.get("name"))
                    elif 'control' in signal:
                        control_bit += control_header(
                            signal.get("comment"), signal.get("name"))
                    elif 'calibration' in signal:
                        control_bit += calibration_header(
                            signal.get("comment"), signal.get("name"))

    text = f"""\
# ifndef CANBUS_H
# define CANBUS_H

# include <stdint.h>
# include <stdbool.h>
{set}
{get}
{control_bit}
# endif /* CANBUS_H */\
"""
    return text
