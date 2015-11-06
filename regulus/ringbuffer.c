#include <stdint.h>
#include <stdbool.h>

#include "ringbuffer.h"

void ringbuffer_configure(ringbuffer_t* rbuffer, uint8_t* user_data, uint16_t len) {
    rbuffer->data = user_data;
    rbuffer->sizeof_data = len;
    rbuffer->push_ptr = user_data;
    rbuffer->pop_ptr  = user_data;
}
bool ringbuffer_is_empty(ringbuffer_t* rbuffer) {
    return (rbuffer->push_ptr == rbuffer->pop_ptr);

}
void ringbuffer_push(ringbuffer_t* rbuffer, uint8_t character) {

    if (rbuffer->push_ptr >= (rbuffer->data + rbuffer->sizeof_data) ) {
        rbuffer->push_ptr = rbuffer->data;
    }

    *(rbuffer->push_ptr) = character;
    rbuffer->push_ptr++;

    //
    // if (rbuffer->current_index == rbuffer->tx_index) {
    //     // overflow -> set tx_index so that the maximum of data is kept in the ringbuffer
    //     ringbuffer_pop(rbuffer);
    // }
}
uint8_t ringbuffer_pop(ringbuffer_t* rbuffer) {
    uint8_t c;
    if (rbuffer->pop_ptr  >= (rbuffer->data + rbuffer->sizeof_data) ) {
        rbuffer->pop_ptr = rbuffer->data;
    }
    c = *rbuffer->pop_ptr;
    rbuffer->pop_ptr++;
    return c;
}
