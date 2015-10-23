#include "main.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "py/nlr.h"
#include "py/compile.h"
#include "py/runtime.h"
#include "py/repl.h"
#include "py/gc.h"
#include "pyexec.h"

USBD_HandleTypeDef USBD_Device;


uint8_t CDC_BUF[128];

static char *stack_top;
static char heap[2048];

int main(void) {
	int stack_dummy;
	stack_top = (char*)&stack_dummy;

	// Initialize the CDC Application
	USBD_Init(&USBD_Device,&USBD_CDC_Descriptor,0);
	// Add Supported Class
	USBD_RegisterClass(&USBD_Device,&USBD_CDC);
	// Add CDC Interface Class
	USBD_CDC_RegisterInterface(&USBD_Device,&USBD_CDC_fops);
	// Start Device Process
	USBD_Start(&USBD_Device);

	gc_init(heap, heap + sizeof(heap));
	mp_init();
	// pyexec_event_repl_init();
	// for (;;) {
	// 	int c = mp_hal_stdin_rx_chr();
	// 	if (pyexec_event_repl_process_char(c)) {
	// 		break;
	// 	}
	// }
	// #else
	pyexec_friendly_repl();
	// #endif
	mp_deinit();
	return 0;
}


	// // Stuff the buffer
	// CDC_BUF[0]  = 'H';
	// CDC_BUF[1]  = 'E';
	// CDC_BUF[2]  = 'L';
	// CDC_BUF[3]  = 'L';
	// CDC_BUF[4]  = 'O';
	// CDC_BUF[5]  = ' ';
	// CDC_BUF[6]  = 'C';
	// CDC_BUF[7]  = 'D';
	// CDC_BUF[8]  = 'C';
	// CDC_BUF[9]  = '\r';
	// CDC_BUF[10] = '\n';
	//
	// uint32_t i;
	// while(1) {
	// 	CDC_Itf_Transmit(CDC_BUF,11);
	// 	for (i = 0x008FFFFF; i--; );
	// }
// }

void gc_collect(void) {
    // TODO possibly need to trace registers
    void *dummy;
    gc_collect_start();
    // Node: stack is ascending
    gc_collect_root(&dummy, ((mp_uint_t)&dummy - (mp_uint_t)MP_STATE_VM(stack_top)) / sizeof(mp_uint_t));
    gc_collect_end();
}



mp_lexer_t *mp_lexer_new_from_file(const char *filename) {
    return NULL;
}

mp_import_stat_t mp_import_stat(const char *path) {
    return MP_IMPORT_STAT_NO_EXIST;
}

mp_obj_t mp_builtin_open(uint n_args, const mp_obj_t *args, mp_map_t *kwargs) {
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_KW(mp_builtin_open_obj, 1, mp_builtin_open);

void nlr_jump_fail(void *val) {
    printf("NLR jump failed\n");
    for (;;) {
    }
}

void __assert_func(const char *file, int line, const char *func, const char *expr) {

    printf("Assertion failed: %s, file %s, line %d\n", expr, file, line);
    while (1);
}
