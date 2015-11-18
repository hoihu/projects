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
bool ringbuffer_push(ringbuffer_t* rbuffer, uint8_t character);
uint8_t ringbuffer_pop(ringbuffer_t* rbuffer);
uint16_t ringbuffer_available_space(ringbuffer_t* rbuffer);

#endif // __RINGBUFFER__
