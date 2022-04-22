from cgitb import text
from math import ceil
from textwrap import dedent

BYTE_BITS: int = 8


def get_content(node, mode, messages):
    text = ""
    text += generate_head(mode)
    text += generate_messages(messages)
    text += generate_can_signal_read()
    text += generate_can_signal_write()
    text += generate_can_service_init(node, mode, messages)
    text += generate_can_service_run(node, mode, messages)
    return text


def generate_head(mode):
    text = ""
    if mode == "dev":
        text = dedent(f'''\
            #include "can_signal.h"
            #include "can_service.h"

            #define BYTE_BITS (8U)

            typedef struct
            {{
                uint32_t id;
                uint16_t timestamp;
                struct
                {{
                    uint8_t extended : 1;
                    uint8_t remote : 1;
                    uint8_t overrun : 1;
                    uint8_t reserved : 5;
                }} flags;
                uint8_t len;
                uint8_t buf[8];
            }} CAN_message_t;
        ''')
    else:
        text = dedent(f'''\
            #include "FlexCAN.h"
            #include "can_signal.h"
            #include "can_service.h"

            #define BYTE_BITS (8U)
            #define BAUD_RATE (250000U)
            #define WRITES_PER_READ (10U)
        ''')
    return text


def generate_messages(messages):
    can_messages = ""

    for i, message in enumerate(messages):
        can_messages += f"\t{{{generate_message(message)}}}"

        if i != len(messages)-1:
            can_messages += f',\n'

    return dedent(f'''
static CAN_message_t messages[] = {{
{can_messages}}};
        ''')


def generate_message(message):
    m = f".id = {message['id']},"
    m += f" .timestamp = 0,"
    m += f" .flags = {{.extended = 0, .remote = 0, .overrun = 0, .reserved = 0}},"
    m += f" .len = {bits_to_bytes(message['signals'][-1]['start'] + message['signals'][-1]['length'])},"
    m += f" .buf = {{0}}"
    return m


def bits_to_bytes(bits):
    return ceil(bits / float(BYTE_BITS))


def generate_can_signal_read():
    return dedent(f'''
        uint64_t can_signal_read(uint8_t msg_index, uint8_t start, uint8_t length)
        {{
            uint64_t value = 0;
            uint8_t pos = start % BYTE_BITS;
            uint8_t index = start / BYTE_BITS;

            for (uint8_t i = 0; i < length; i++)
            {{
                uint8_t bit = (messages[msg_index].buf[index] >> pos) & 1U;

                if (bit == 1U)
                {{
                    value |= (1ULL << i);
                }}

                pos++;
                if (pos == BYTE_BITS)
                {{
                    pos = 0;
                    index++;
                }}
            }}

            return value;
        }}
    ''')


def generate_can_signal_write():
    return dedent('''
        void can_signal_write(uint8_t msg_index, uint8_t start, uint8_t length, uint64_t value)
        {
            uint8_t pos = start % BYTE_BITS;
            uint8_t index = start / BYTE_BITS;

            for (uint8_t i = 0; i < length; i++)
            {
                uint8_t bit = (uint8_t)((value >> i) & 1U);

                if (bit == 0)
                {
                    messages[msg_index].buf[index] &= ~(1U << pos);
                }
                else
                {
                    messages[msg_index].buf[index] |= (1U << pos);
                }

                pos++;
                if (pos == BYTE_BITS)
                {
                    pos = 0;
                    index++;
                }
            }
        }
    ''')


def get_rx_messages(node, messages):
    rx_ids = []
    for message in messages:
        for signal in message['signals']:
            if node in signal['getters']:
                rx_ids.append(message['id'])
                break
    return rx_ids


def get_rx_indeces(node, messages):
    rx_indices = []
    for index, message in enumerate(messages):
        for signal in message['signals']:
            if node in signal['getters']:
                rx_indices.append(index)
                break
    return rx_indices


def get_tx_indeces(node, messages):
    tx_indices = []
    for index, message in enumerate(messages):
        if node == message['setter']:
            tx_indices.append(index)
    return tx_indices


def generate_can_service_init(node, mode, messages):
    text = ""
    if mode == "dev":

        text = dedent('''
            void can_service_init(void)
            {
                
            }
        ''')
    else:
        rx_ids = get_rx_messages(node, messages)

        text += dedent('''
            void can_service_init(void)
            {
                Can0.begin(BAUD_RATE);

                CAN_filter_t filter = {.id = 0x7FF, .flags = {.extended = 1, .remote = 0, .reserved = 0}};

                for (uint8_t i = 0; i < NUM_MAILBOXES; ++i)
                {
                    Can0.setFilter(filter, i);
                    Can0.setMask(0x000, i);
                }
                filter.flags.extended = 0;

                ''')
        for index, value in enumerate(rx_ids):
            text += '\tfilter.id = ' + value + ';\n'
            text += '\tCan0.setFilter(filter, {0});\n'.format(index)
            text += '\tCan0.setMask({0} << 18, {1});\n\n'.format(value, index)

        text = text[:-1] + '}\n'
    return text


def generate_can_service_run(node, mode, messages):
    text = ""
    if mode == "dev":
        text = dedent('''
            void can_service_run(void)
            {

            }
        ''')
    else:
        tx_indeces = get_tx_indeces(node, messages)
        tx_indeces = [str(x) for x in tx_indeces]
        text = dedent('''
            void can_service_run(void)
            {{
                static uint8_t counter = 0;

                const uint8_t tx_index[{0}] = {{{1}}};
                for (uint8_t i = 0; i < {0}; i++)
                {{
                    Can0.write(messages[tx_index[i]]);
                }}
                counter++;
            '''.format(len(tx_indeces), ', '.join(tx_indeces)))

        rx_indeces = get_rx_indeces(node, messages)
        rx_indeces = [str(x) for x in rx_indeces]

        text += '''
    if (counter == WRITES_PER_READ)
    {{
        counter = 0;
        CAN_message_t msg;
        const uint8_t rx_index[{0}] = {{{1}}};
        while (Can0.read(msg))
        {{
            for (uint8_t i = 0; i < {0}; i++)
            {{
                if (messages[rx_index[i]].id == msg.id)
                {{
                    messages[rx_index[i]] = msg;
                }}
            }}
        }}
    }}\n}}'''.format(len(rx_indeces), ', '.join(rx_indeces))
    return text
