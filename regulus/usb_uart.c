#include <unistd.h>
#include <string.h>
#include "mpconfig.h"
#include "main.h"
#include "ringbuffer.h"
#include "usbd_cdc_interface.h"

extern ringbuffer_t rx_ringbuffer;
extern bool CDC_is_busy;
extern volatile uint32_t rec_length;

int usb_vcp_recv_byte(uint8_t *c) {
    if (!ringbuffer_is_empty(&rx_ringbuffer)) {
        *c = ringbuffer_pop(&rx_ringbuffer);
        return 1;
    }
    return 0;

}

void usb_vcp_send_strn(const char *str, int len) {
    while (len--) {
        ringbuffer_push(&tx_ringbuffer, *str++);
    }
    if (!CDC_is_busy) {
        CDC_send_packet();
    }
}

void usb_vcp_send_strn_cooked(const char *str, int len) {
    while (len--) {
        if (*str == '\n') {
            ringbuffer_push(&tx_ringbuffer, *(uint8_t*)("\r"));
            // mp_hal_stdout_tx_strn("\r", 1);
        }
        ringbuffer_push(&tx_ringbuffer, *str++);
    }
    if (!CDC_is_busy) {
        CDC_send_packet();
    }
}

// void usb_vcp_set_interrupt_char(int c) {
//     if (c != -1) {
//         mp_obj_exception_clear_traceback(MP_STATE_PORT(mp_const_vcp_interrupt));
//     }
//     USBD_CDC_SetInterrupt(c, MP_STATE_PORT(mp_const_vcp_interrupt));
// }

int mp_hal_stdin_rx_chr(void) {
    for (;;) {
        uint8_t c;
        if (usb_vcp_recv_byte(&c) != 0) {
            return c;
        }
        __WFI();
    }
}

void mp_hal_stdout_tx_str(const char *str) {
    mp_hal_stdout_tx_strn(str, strlen(str));
}

void mp_hal_stdout_tx_strn(const char *str, mp_uint_t len) {
    usb_vcp_send_strn(str,len);
}

void mp_hal_stdout_tx_strn_cooked(const char *str, mp_uint_t len) {
    usb_vcp_send_strn_cooked(str, len);
}
