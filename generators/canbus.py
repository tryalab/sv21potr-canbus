
def set_function(prototype, valid, if_float_multiply, index, start, length):
    text = \
        f"""
{prototype}
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


def get_function(prototype, type, if_float_devide, index, start, length):
    text = \
        f"""
{prototype}
{{
    return ({type})can_signal_read({index}, {start}, {length}){if_float_devide};
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


def calibration_function(name, control_bit_function):
    text = \
        f"""
bool canbus_is_{name}_valid(void)
{{
    return {control_bit_function};
}}
              """
    return text


def set_min_function(prototype_set, prototype_get, valid, if_float_multiply, index, start, length):

    text = \
        f"""
{prototype_set}
{{
    bool status = false;

    if ({valid})
    {{
        uint8_t max_value = {prototype_get[prototype_get.find('canbus'):prototype_get.find('min')] + "max"}();

        if (max_value >= value)
        {{\
            {if_float_multiply}
            can_signal_write({index}, {start}, {length}, (uint64_t)value);
            can_signal_write({index}, {start + length}, 1, 1);
            status = true;
        }}
    }}

    return status;
}}
              """
    return text


def set_only_min_or_max_function(prototype_set, valid, if_float_multiply, index, start, length):

    text = \
        f"""
{prototype_set}
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


def set_max_function(prototype_set, prototype_get, valid, if_float_multiply, index, start, length):
    text = \
        f"""
{prototype_set}
{{
    bool status = false;

    if ({valid})
    {{
        uint8_t min_value = {prototype_get[prototype_get.find('canbus'):prototype_get.find('max')] + "min"}();

        if (min_value <= value)
        {{\
            {if_float_multiply}
            can_signal_write({index}, {start}, {length}, (uint64_t)value);
            can_signal_write({index}, {start + length}, 1, 1);
            status = true;
        }}
    }}

    return status;
}}
              """
    return text


def get_canbus_source(node, mode, messages):
    get = ''
    set = ''
    control_bit = ''

    #list_min_max = []
    # for index, message in enumerate(messages):
    #    for signal in message["signals"]:
    #        if 'calibration' in signal:
    #            list_min_max.append(signal.get('name'))

    # print(list_min_max)

    for index, message in enumerate(messages):
        for signal_index, signal in enumerate(message["signals"]):

            name = signal.get("name")
            type = signal.get("type")
            start = signal.get("start")
            length = signal.get("length")

            if message['setter'] == node or node in signal['getters']:
                if "range" in signal:
                    low_boundary = str(signal["range"][0])
                    high_boundary = str(signal["range"][-1])
                elif "values" in signal:
                    high_boundary = signal["values"][-1]
                if type == "float":
                    if_float_multiply = '''\n\t\tvalue *= 10;'''
                    if_float_devide = " / 10"
                else:
                    if_float_multiply = ""
                    if_float_devide = ""

                # decide the value range for validity
                valid = ''
                if 'range' in signal:
                    if signal["range"][0] != 0:
                        valid = f"""{low_boundary} <= value && value <= {high_boundary}"""
                    else:
                        valid = f"""value <= {high_boundary}"""
                else:
                    valid = f"""value <= {high_boundary}"""

                # to remove control bit from message
                if 'update' in signal or 'control' in signal or 'calibration' in signal:
                    length -= 1

                # generate setters and getters function
                if message['setter'] == node and node in signal['getters']:
                    prototype_set = f"""bool canbus_set_{name}({type} value)"""
                    prototype_get = f"""{type} canbus_get_{name}(void)"""

                elif message['setter'] == node and node not in signal['getters']:
                    prototype_set = f"""bool canbus_set_{name}({type} value)"""
                    prototype_get = ''
                    if mode == 'dev':
                        prototype_get = f"""{type} canbus_test_get_{name}(void)"""

                elif message['setter'] != node and node in signal['getters']:
                    prototype_set = ''
                    prototype_get = f"""{type} canbus_get_{name}(void)"""
                    if mode == 'dev':
                        prototype_set = f"""bool canbus_test_set_{name}({type} value)"""

                if prototype_set != '':
                    if 'calibration' in signal:

                        previous_name = message["signals"][signal_index-1]['name']
                        next_name = ''
                        if message["signals"][-1]['name'] != name:
                            next_name = message["signals"][signal_index + 1]['name']

                        if name.find('min') != -1:
                            if previous_name.find('max') != -1:
                                previous_name = previous_name.replace(previous_name[len(previous_name) - 3:], "min")
                            if next_name.find('max') != -1:
                                next_name = next_name.replace(next_name[len(next_name) - 3:], "min")

                            if name == previous_name or name == next_name:
                                set += set_min_function(prototype_set, prototype_get, valid, if_float_multiply, index, start, length)
                            else:
                                set += set_only_min_or_max_function(prototype_set, valid, if_float_multiply, index, start, length)

                        if name.find('max') != -1:
                            if previous_name.find('min') != -1:
                                previous_name = previous_name.replace(previous_name[len(previous_name) - 3:], "max")
                            if next_name.find('min') != -1:
                                next_name = next_name.replace(next_name[len(next_name) - 3:], "max")

                            if name == previous_name or name == next_name:
                                set += set_max_function(prototype_set, prototype_get, valid, if_float_multiply, index, start, length)
                            else:
                                set += set_only_min_or_max_function(prototype_set, valid, if_float_multiply, index, start, length)
                    else:
                        set += set_function(prototype_set, valid, if_float_multiply, index, start, length)

                if prototype_get != '':
                    get += get_function(prototype_get, type, if_float_devide, index, start, length)

                # add functions for update, control and calibration (_updated, _enabled, _valid)
                control_bit_position = start + length - 1
                control_bit_function = f"""can_signal_read({index}, {control_bit_position}, 1)"""
                if node in signal['getters']:
                    if 'update' in signal:
                        control_bit += update_function(name,
                                                       control_bit_function)

                    elif 'control' in signal:
                        control_bit += control_function(name,
                                                        control_bit_function)

                    elif 'calibration' in signal:
                        control_bit += calibration_function(
                            name, control_bit_function)

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

            name = signal.get("name")
            type = signal.get("type")
            comment = signal.get("comment")

            if message['setter'] == node or node in signal['getters']:

                if message['setter'] == node and node in signal['getters']:
                    set += set_header(comment, name, type)
                    get += get_header(comment, name, type)

                elif message['setter'] == node and node not in signal['getters']:
                    set += set_header(comment, name, type)

                    if mode == 'dev':
                        get += get_test_double_header(comment, name, type)

                elif message['setter'] != node and node in signal['getters']:
                    get += get_header(comment, name, type)

                    if mode == 'dev':
                        set += set_test_double_header(comment, name, type)

                if node in signal['getters']:
                    if 'update' in signal:
                        control_bit += update_header(comment, name)
                    elif 'control' in signal:
                        control_bit += control_header(comment, name)
                    elif 'calibration' in signal:
                        control_bit += calibration_header(comment, name)

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
