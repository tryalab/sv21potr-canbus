#ifndef CAN_SIGNAL_H
#define CAN_SIGNAL_H

#include <stdint.h>

/**
 * @brief This function is used to insert a signal with a specific length in a specific message from a specific position.
 *
 * @param msg_index The message index
 * @param start The start position of the signal in the message
 * @param length The length of the signal
 * @param value The value of the signal
 */
void can_signal_write(uint8_t msg_index, uint8_t start, uint8_t length, uint64_t value);

/**
 * @brief This function is used to extrac a signal with a specific length in a specific message from a specific position.
 *
 * @param msg_index The message index
 * @param start The start position of the signal in the message
 * @param length The length of the signal
 * @return uint64_t The return value of the signal from the CAN bus
 */
uint64_t can_signal_read(uint8_t msg_index, uint8_t start, uint8_t length);

#endif /* CAN_SIGNAL_H */
