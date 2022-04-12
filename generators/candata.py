

def get_text(name, struct_name):
   text = f"void get_{name}_text(char *text, {struct_name} {name});"
   return text

def changed(name, struct_name):
   text = f"bool is_{name}_changed({struct_name} previous, {struct_name} current);"
   return text

def struct(struct_members, struct_name):
   text = \
f"""
typedef struct
{{
    {struct_members}
}}{struct_name}
"""
   return text

def get_candata_header(messages):
    for message in messages:
        for signal in message["signals"]:


            text= ""
    return text


def get_candata_source(messages):
    text = """\
#include <stdio.h>
#include <stdint.h>
#include "canbus.h"

static char buffer[500] = {0};
static uint8_t counter = 0;

static void insert_float_to_buffer(float value)
{
    char str[10];
    sprintf(str, "%.1f", value); // integer to string
    for (int i = 0; i < 10; i++)
    {
        if (str[i] != '\\0')
        {
            buffer[counter] = str[i];
            counter++;
        }
        else
        {
            break;
        }
    }
    buffer[counter] = '|';
    counter++;
}

char *get_I2C_buffer(void)
{
    return buffer;
}

void can_data_get_temp(void)
{
    float value = canbus_get_temperature();
    insert_float_to_buffer(value);
}"""
    return text
