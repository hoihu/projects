#ifndef __RINGBUFFER__
#define __RINGBUFFER__

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t* data;
    uint16_t sizeof_data;
    uint8_t* push_ptr;
    uint8_t* pop_ptr;
} ringbuffer_t;


void ringbuffer_configure(ringbuffer_t* rbuffer, uint8_t* user_data, uint16_t length);
bool ringbuffer_is_empty(ringbuffer_t* rbuffer);
void ringbuffer_push(ringbuffer_t* rbuffer, uint8_t character);
uint8_t ringbuffer_pop(ringbuffer_t* rbuffer);

#endif // __RINGBUFFER__
