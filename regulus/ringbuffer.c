/*
 * This file is part of the Micro Python project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2013, 2014 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

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

uint16_t ringbuffer_available_space(ringbuffer_t* rbuffer) {
    if (rbuffer->push_ptr > rbuffer->pop_ptr) {
        return rbuffer->sizeof_data - (rbuffer->push_ptr - rbuffer->pop_ptr);
    }
    else 
        return rbuffer->pop_ptr - rbuffer->push_ptr;
}

bool ringbuffer_push(ringbuffer_t* rbuffer, uint8_t character) {

    if (rbuffer->push_ptr >= (rbuffer->data + rbuffer->sizeof_data) ) {
        rbuffer->push_ptr = rbuffer->data;
    }

    *(rbuffer->push_ptr) = character;
    rbuffer->push_ptr++;
    
    if (rbuffer->push_ptr == rbuffer->pop_ptr) {
        // ringbuffer is now full -> signal this as fault but
        // push it on the buffer -> this will overwrite oldest data in buffer
        ringbuffer_pop(rbuffer);
        return false;
    }
    
    return true;
}
uint8_t ringbuffer_pop(ringbuffer_t* rbuffer) {
    uint8_t c;
    if (rbuffer->pop_ptr  >= (rbuffer->data + rbuffer->sizeof_data) ) {
        // wraparound
        rbuffer->pop_ptr = rbuffer->data;
    }
    c = *rbuffer->pop_ptr;
    rbuffer->pop_ptr++;
    return c;
}
