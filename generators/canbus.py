def set_function(name, type, valid, if_float_multiply, index, start, length):
    text = \
        f"""
bool canbus_set_{name}({type} value)
{{
    bool status = false;

    if ({valid})
    {{\
        {if_float_multiply}
        can_signal_write({index}, {start}, {length}, (uint64_t)value);
        status = true;
    }}

    return status;
}}
              """
    return text

def set_test_function(name, type, valid, if_float_multiply, index, start, length):
    text = \
        f"""
bool canbus_test_set_{name}({type} value)
{{
    bool status = false;

    if ({valid})
    {{\
        {if_float_multiply}
        can_signal_write({index}, {start}, {length}, (uint64_t)value);
        status = true;
    }}

    return status;
}}
              """
    return text

def get_function(name, type, return_line):
    text = \
        f"""
{type} canbus_get_{name}(void)
{{
    {return_line}
}}
              """
    return text

def get_test_function(name, type, return_line):
    text = \
        f"""
{type} canbus_test_get_{name}(void)
{{
    {return_line}
}}
              """
    return text

def update_function(name, control_bit_function):
    text = \
        f"""
bool canbus_is_{name}_updated(void)
{{
    bool status = false;
    static uint8_t previous_value = 0;
    uint8_t value = {control_bit_function};

    if(previous_value != value)
    {{
        previous_value = value;
        status = true;
    }}

    return status;
}}
              """
    return text

def control_function(name, control_bit_function):
    text = \
        f"""
bool canbus_is_{name}_enabled(void)
{{
    return {control_bit_function};
}}
              """
    return text

def control_test_function(name, control_bit_function):
    text = \
        f"""
bool canbus_test_is_{name}_enabled(void)
{{
    return {control_bit_function};
}}
              """
    return text

def control_set_function(replace_name, control_bit_function):
    text = \
        f"""
void canbus_set_{replace_name}(bool value)
{{
    {control_bit_function};
}}
              """
    return text

def control_test_set_function(replace_name, control_bit_function):
    text = \
        f"""
void canbus_test_set_{replace_name}(bool value)
{{
    {control_bit_function};
}}
              """
    return text

def calibration_function(name, control_bit_function):
    text = \
        f"""
bool canbus_is_{name}_valid(void)
{{
    return {control_bit_function};
}}
              """
    return text

def set_update_function(name, type, valid, if_float_multiply, index, start, length):

    text = \
        f"""
bool canbus_set_{name}({type} value)
{{
    bool status = false;
    static uint8_t update = 0;
    if ({valid})
    {{\
        {if_float_multiply}
        update = !update;
        can_signal_write({index}, {start}, {length}, (uint64_t)value);
        can_signal_write({index}, {start + length}, 1, (uint64_t)update);
        status = true;
    }}

    return status;
}}
              """
    return text

def set_test_update_function(name, type, valid, if_float_multiply, index, start, length):

    text = \
        f"""
bool canbus_test_set_{name}({type} value)
{{
    bool status = false;
    static uint8_t update = 0;
    if ({valid})
    {{\
        {if_float_multiply}
        update = !update;
        can_signal_write({index}, {start}, {length}, (uint64_t)value);
        can_signal_write({index}, {start + length}, 1, (uint64_t)update);
        status = true;
    }}

    return status;
}}
              """
    return text

def set_min_max_function(name, type, valid, if_float_multiply, index, start, length):

    text = \
        f"""
bool canbus_set_{name}({type} value)
{{
    bool status = false;

    if ({valid})
    {{\
        {if_float_multiply}
        can_signal_write({index}, {start}, {length}, (uint64_t)value);
        can_signal_write({index}, {start + length}, 1, 1);
        status = true;
    }}

    return status;
}}
              """
    return text

def set_test_min_max_function(name, type, valid, if_float_multiply, index, start, length):

    text = \
        f"""
bool canbus_test_set_{name}({type} value)
{{
    bool status = false;

    if ({valid})
    {{\
        {if_float_multiply}
        can_signal_write({index}, {start}, {length}, (uint64_t)value);
        can_signal_write({index}, {start + length}, 1, 1);
        status = true;
    }}

    return status;
}}
              """
    return text

def convert_function():
    text = """ 

static int64_t convert(uint64_t value, uint8_t length)
{
    if (value & (1ULL << (length - 1)))
    {
        value |= (~0ULL << length);
    }

    return (int64_t)value;
}"""
    return text

def get_canbus_source(node, mode, messages):
    get = ''
    set = ''
    control_bit = ''
    convert = ''

    for index, message in enumerate(messages):
        for signal in message['signals']:

            name = signal.get('name')
            type = signal.get('type')
            start = signal.get('start')
            length = signal.get('length')

            if message['setter'] == node or node in signal['getters']:

                if type == 'float':
                    if_float_multiply = "\n\t\tvalue *= 10;"
                    if_float_devide = " / 10"
                else:
                    if_float_multiply = ""
                    if_float_devide = ""
            
                    # to remove control bit from message
                if 'update' in signal or 'control' in signal or 'calibration' in signal:
                    length -= 1

                    # generate functions for update, control and calibration (_updated, _enabled, _valid)
                control_bit_position = start + length
                control_bit_read_function = f"can_signal_read({index}, {control_bit_position}, 1)"

                valid = ''
                # decide the value range for validity
                if 'range' in signal:
                    low_boundary = str(signal['range'][0])
                    high_boundary = str(signal['range'][-1])

                    if signal['range'][0] != 0:
                        valid = f"{low_boundary} <= value && value <= {high_boundary}"
                    else:
                        valid = f"value <= {high_boundary}"

                    # if negative value in range use convert function
                    if signal['range'][0] < 0:
                        return_text = f"return ({type})convert(can_signal_read({index}, {start}, {length}), {length}){if_float_devide};"
                        convert = convert_function()
                    else:
                        return_text = f"return ({type})can_signal_read({index}, {start}, {length}){if_float_devide};"
                else:
                    high_boundary = signal['values'][-1]
                    valid = f"value <= {high_boundary}"
                    return_text = f"return ({type})can_signal_read({index}, {start}, {length}){if_float_devide};"
                
                if 'control' in signal:
                    control_write_function = f"can_signal_write({index}, {control_bit_position}, 1, (uint64_t)value)"
                    if "state" in name:
                        replace_name = name.replace(name[len(name) - 5:], "mode")
                    else:
                        replace_name = name + "_mode"

                # generate setters, getters and control bit functions
                if message['setter'] == node:
                    if 'control' in signal:
                        control_bit += control_set_function(replace_name, control_write_function)
                    if 'calibration' in signal:
                        set += set_min_max_function(name, type, valid, if_float_multiply, index, start, length)
                    elif 'update' in signal:
                        set += set_update_function(name, type, valid, if_float_multiply, index, start, length)
                    else:
                        set += set_function(name, type, valid, if_float_multiply, index, start, length)
                    if node not in signal['getters']:
                        if mode == 'dev':
                            get += get_test_function(name, type, return_text)
                            if 'control' in signal:
                                control_bit += control_test_function(replace_name, control_bit_read_function)
                if node in signal['getters']:
                    get += get_function(name, type, return_text)
                    if message['setter'] != node:
                        if mode == 'dev':
                            if 'calibration' in signal:
                                set += set_test_min_max_function(name, type, valid, if_float_multiply, index, start, length)
                            elif 'update' in signal:
                                set += set_test_update_function(name, type, valid, if_float_multiply, index, start, length)
                            elif 'control' in signal:
                                set += control_test_set_function(replace_name, control_write_function)
                            else:
                                set += set_test_function(name, type, valid, if_float_multiply, index, start, length)
                    
                    if 'update' in signal:
                        control_bit += update_function(name, control_bit_read_function)
                    elif 'control' in signal:
                        control_bit += control_function(replace_name, control_bit_read_function)
                    elif 'calibration' in signal:
                        control_bit += calibration_function(name, control_bit_read_function)

    text = f'''\
#include "canbus.h"
#include "common.h"
#include "can_signal.h"\
{convert}
{set}
{get}
{control_bit}\
'''
    return text

def set_test_double_header(comment, ret_desc, name, type):
    text = \
        f"""
/**
 * @brief This function is used as test double to set {comment}.
 * @param value The value to set.
 * @return true if value is {ret_desc}; otherwise false.
 */
bool canbus_test_set_{name}({type} value);
              """
    return text

def set_header(comment, ret_desc, name, type):
    text = \
        f"""
/**
 * @brief This function is used to set {comment}.
 * @param value The value to set.
 * @return true if value is {ret_desc}; otherwise false.
 */
bool canbus_set_{name}({type} value);
              """
    return text

def get_test_double_header(comment, ret_desc, name, type):
    text = \
        f"""
/**
 * @brief This function is used as test double to get {comment}.
 * @return {type} The {comment} which is {ret_desc}.
 */
{type} canbus_test_get_{name}(void);
              """
    return text

def get_header(comment, ret_desc, name, type):
    text = \
        f"""
/**
 * @brief This function is used to get {comment}.
 * @return {type} The {comment} which is {ret_desc}.
 */
{type} canbus_get_{name}(void);
              """
    return text

def update_header(comment, name):
    text = \
        f"""
/**
 * @brief This function is used to check if {comment} is updated.
 * @return true if signal is updated; otherwise false
 */
bool canbus_is_{name}_updated(void);
              """
    return text

def control_header(name, replace_name):
    text = \
        f"""
/**
 * @brief This function is used to check if {name} is enabled.
 * @return true if signal is enabled; otherwise false
 */
bool canbus_is_{replace_name}_enabled(void);
              """
    return text

def control_test_header(name, replace_name):
    text = \
        f"""
/**
 * @brief This function is a test double and is used to check if {name} is enabled.
 * @return true if signal is enabled; otherwise false
 */
bool canbus_test_is_{replace_name}_enabled(void);
              """
    return text

def set_control_header(name, replace_name):
    text = \
        f"""
/**
 * @brief This function is used to set the mode of {name}.
 * @param value The value to set.
 */
void canbus_set_{replace_name}(bool value);
              """
    return text

def set_test_control_header(name, replace_name):
    text = \
        f"""
/**
 * @brief This function is used as a test double to set the mode of {name}.
 * @param value The value to set.
 */
void canbus_test_set_{replace_name}(bool value);
              """
    return text

def calibration_header(comment, name):
    text = \
        f"""
/**
 * @brief This function is used to check if {comment} is valid.
 * @return true if the calibration value is valid; otherwise false.
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
        for signal in message['signals']:

            name = signal.get('name')
            type = signal.get('type')
            comment = signal.get('comment')

            if message['setter'] == node or node in signal['getters']:
                description = ""
                if 'range' in signal:
                    description = f"in the range of [{signal['range'][0]}, {signal['range'][1]}]"
                else:
                    description = ', '.join(signal['values'][:-1])
                    description += ' or ' + signal['values'][-1]
                
                if 'state' in name:
                    replace_name = name.replace(name[len(name) - 5:], "mode")
                else:
                    replace_name = name + "_mode"

                if message['setter'] == node:
                    set += set_header(comment, description, name, type)
                    if 'control' in signal:
                        control_bit += set_control_header(name, replace_name)
                    if node not in signal['getters']:
                        if mode == 'dev':
                            get += get_test_double_header(comment, description, name, type)
                            if 'control' in signal:
                                control_bit += control_test_header(name, replace_name)
                if node in signal['getters']:
                    get += get_header(comment, description, name, type)
                    if message['setter'] != node:
                        if mode == 'dev':
                            if 'control' in signal:
                                set += set_test_control_header(name, replace_name)
                            else:
                                set += set_test_double_header(comment, description, name, type)

                    if 'update' in signal:
                        control_bit += update_header(comment, name)
                    elif 'control' in signal:
                        control_bit += control_header(name, replace_name)
                    elif 'calibration' in signal:
                        control_bit += calibration_header(comment, name)

    text = f"""\
#ifndef CANBUS_H
#define CANBUS_H

#include <stdint.h>
#include <stdbool.h>
{set}
{get}
{control_bit}
#endif /* CANBUS_H */\
"""
    return text
