#include "main.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "usbd_cdc_interface.h"
#include "py/nlr.h"
#include "py/compile.h"
#include "readline.h"
#include "py/runtime.h"
#include "py/repl.h"
#include "py/gc.h"
#include "pyexec.h"

USBD_HandleTypeDef USBD_Device;
extern uint8_t* UserRXBuf;
static char *stack_top;
static char heap[2048];
// extern volatile uint16_t is_initalized;

void SystemClock_Config(void);

// #define MICROPY_REPL_EVENT_DRIVEN 1

int main(void) {
	// uint16_t i;
	int stack_dummy;
	stack_top = (char*)&stack_dummy;

	HAL_Init();

	/* Configure the system clock to 32 MHz */
	SystemClock_Config();

	gc_init(heap, heap + sizeof(heap));
	mp_init();
	readline_init0();

	pyexec_event_repl_init();

	/* Init Device Library */
	USBD_Init(&USBD_Device, &VCP_Desc, 0);

	/* Add Supported Class */
	USBD_RegisterClass(&USBD_Device, USBD_CDC_CLASS);

	/* Add CDC Interface Class */
	USBD_CDC_RegisterInterface(&USBD_Device, (USBD_CDC_ItfTypeDef *)&USBD_CDC_fops);

	/* Start Device Process */
	USBD_Start(&USBD_Device);


	// is_initalized = 1;

	for (;;) {

		// pyexec_event_repl_init();
		USBD_CDC_TxAlways((const uint8_t*)"test", 4);

		// mp_hal_stdout_tx_str("MicroPython \r\n");
		// // if (usb_char_received) {
		// CDC_Itf_Transmit(UserRXBuf,0);
		// }
		// uint8_t c = mp_hal_stdin_rx_chr();
		// CDC_Itf_Transmit(CDC_BUF,11);
        // CDC_Itf_Transmit(&c,1);
        // CDC_Itf_Transmit(&c,1);
        // CDC_Itf_Transmit(&c,1);

		// c=c*2;
		// if (pyexec_event_repl_process_char(c)) {
		// 	break;
		// }
	}
	// #else
	// pyexec_friendly_repl();
	// #endif
	mp_deinit();
	return 0;
}

/**
  * @brief  System Clock Configuration
  *         The system Clock is configured as follow :
  *            System Clock source            = PLL (HSE)
  *            SYSCLK(Hz)                     = 32000000
  *            HCLK(Hz)                       = 32000000
  *            AHB Prescaler                  = 1
  *            APB1 Prescaler                 = 1
  *            APB2 Prescaler                 = 1
  *            HSE Frequency(Hz)              = 8000000
  *            HSI Frequency(Hz)              = 16000000
  *            HSE PREDIV                     = 1
  *            PLLMUL                         = 12 (if HSE) or 6 (if HSI)
  *            PLLDIV                         = 3
  *            Flash Latency(WS)              = 1
  * @param  None
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};

  /* Enable HSE Oscillator and Activate PLL with HSE as source */
  RCC_OscInitStruct.OscillatorType      = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState            = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState        = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource       = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL          = RCC_PLL_MUL8;
  RCC_OscInitStruct.PLL.PLLDIV          = RCC_PLL_DIV3;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /* Set Voltage scale1 as MCU will run at 32MHz */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /* Poll VOSF bit of in PWR_CSR. Wait until it is reset to 0 */
  while (__HAL_PWR_GET_FLAG(PWR_FLAG_VOS) != RESET) {};

  /* Select PLL as system clock source and configure the HCLK, PCLK1 and PCLK2
  clocks dividers */
  RCC_ClkInitStruct.ClockType = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief  Toggles LEDs to shows user input state.
  * @param  None
  * @retval None
  */
void Toggle_Leds(void)
{
  static uint32_t ticks;

  if(ticks++ == 100)
  {
    // BSP_LED_Toggle(LED1);
    // BSP_LED_Toggle(LED2);
    // BSP_LED_Toggle(LED3);
    // BSP_LED_Toggle(LED4);
    ticks = 0;
  }
}


/**
  * @brief  This function is executed in case of error occurrence.
  * @param  None
  * @retval None
  */
void Error_Handler(void)
{
  /* Turn LED3 on */
  // BSP_LED_On(LED3);
  while (1)
  {
  }
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t* file, uint32_t line)
{
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */

  /* Infinite loop */
  while (1)
  {
  }
}
#endif

void gc_collect(void) {
    //TODO possibly need to trace registers
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
