/**
  ******************************************************************************
  * @file    USB_Device/CDC_Standalone/Src/usbd_cdc_interface.c
  * @author  MCD Application Team
  * @version V1.3.0
  * @date    3-July-2015
  * @brief   Source file for USBD CDC interface
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; COPYRIGHT(c) 2015 STMicroelectronics</center></h2>
  *
  * Licensed under MCD-ST Liberty SW License Agreement V2, (the "License");
  * You may not use this file except in compliance with the License.
  * You may obtain a copy of the License at:
  *
  *        http://www.st.com/software_license_agreement_liberty_v2
  *
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "ringbuffer.h"
#include <stdbool.h>

/** @addtogroup STM32_USB_OTG_DEVICE_LIBRARY
  * @{
  */

/** @defgroup USBD_CDC
  * @brief usbd core module
  * @{
  */

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
#define APP_RX_DATA_SIZE  1024
#define APP_TX_DATA_SIZE  1024

void CDC_Itf_TxFinished(void);
void CDC_send_packet(void);



uint8_t UserRxBuffer[APP_RX_DATA_SIZE];/* Received Data over USB are stored in this buffer */
uint8_t tx_buffer[1024];
uint8_t rx_buffer[1024];
bool CDC_is_busy;

ringbuffer_t tx_ringbuffer;
ringbuffer_t rx_ringbuffer;

/* USB handler declaration */
extern USBD_HandleTypeDef  USBD_Device;
extern void usb_rx_callback(ringbuffer_t*);


/* Private function prototypes -----------------------------------------------*/
static int8_t CDC_Itf_Init     (void);
static int8_t CDC_Itf_DeInit   (void);
static int8_t CDC_Itf_Control  (uint8_t cmd, uint8_t* pbuf, uint16_t length);
static int8_t CDC_Itf_Receive  (uint8_t* pbuf, uint32_t *Len);

USBD_CDC_ItfTypeDef USBD_CDC_fops =
{
  CDC_Itf_Init,
  CDC_Itf_DeInit,
  CDC_Itf_Control,
  CDC_Itf_Receive,
  CDC_Itf_TxFinished
};

/* Private functions ---------------------------------------------------------*/

/**
  * @brief  CDC_Itf_Init
  *         Initializes the CDC media low layer
  * @param  None
  * @retval Result of the opeartion: USBD_OK if all operations are OK else USBD_FAIL
  */
static int8_t CDC_Itf_Init(void)
{
    CDC_is_busy = false;

    ringbuffer_configure(&tx_ringbuffer, tx_buffer, 1024);
    ringbuffer_configure(&rx_ringbuffer, rx_buffer, 1024);
    /*##-5- Set Application Buffers ############################################*/
    USBD_CDC_SetTxBuffer(&USBD_Device, tx_ringbuffer.data, 0);
    USBD_CDC_SetRxBuffer(&USBD_Device, UserRxBuffer);
    return (USBD_OK);
}

/**
  * @brief  CDC_Itf_DeInit
  *         DeInitializes the CDC media low layer
  * @param  None
  * @retval Result of the opeartion: USBD_OK if all operations are OK else USBD_FAIL
  */
static int8_t CDC_Itf_DeInit(void)
{
  return (USBD_OK);
}

/**
  * @brief  CDC_Itf_Control
  *         Manage the CDC class requests
  * @param  Cmd: Command code
  * @param  Buf: Buffer containing command data (request parameters)
  * @param  Len: Number of data to be sent (in bytes)
  * @retval Result of the opeartion: USBD_OK if all operations are OK else USBD_FAIL
  */
static int8_t CDC_Itf_Control (uint8_t cmd, uint8_t* pbuf, uint16_t length)
{
  switch (cmd)
  {
  case CDC_SEND_ENCAPSULATED_COMMAND:
    /* Add your code here */
    break;

  case CDC_GET_ENCAPSULATED_RESPONSE:
    /* Add your code here */
    break;

  case CDC_SET_COMM_FEATURE:
    /* Add your code here */
    break;

  case CDC_GET_COMM_FEATURE:
    /* Add your code here */
    break;

  case CDC_CLEAR_COMM_FEATURE:
    /* Add your code here */
    break;

  case CDC_SET_LINE_CODING:
    break;

  case CDC_GET_LINE_CODING:
    pbuf[0] = (uint8_t)(115200);
    pbuf[1] = (uint8_t)(115200 >> 8);
    pbuf[2] = (uint8_t)(115200 >> 16);
    pbuf[3] = (uint8_t)(115200 >> 24);
    pbuf[4] = 0; // stop bits (1)
    pbuf[5] = 0; // parity (none)
    pbuf[6] = 8; // number of bits (8)

    /* Add your code here */
    break;

  case CDC_SET_CONTROL_LINE_STATE:
    /* Add your code here */
    break;

  case CDC_SEND_BREAK:
     /* Add your code here */
    break;

  default:
    break;
  }

  return (USBD_OK);
}

// const char *test = "TEST YEEAAHH";

void CDC_Itf_TxFinished(void) {
    if (ringbuffer_is_empty(&tx_ringbuffer)) {
        CDC_is_busy = false;
        return;
    }
    CDC_is_busy = true;
    CDC_send_packet();
}

/**
  * @brief  CDC_Itf_DataRx
  *         Data received over USB OUT endpoint are sent over CDC interface
  *         through this function.
  * @param  Buf: Buffer of data to be transmitted
  * @param  Len: Number of data received (in bytes)
  * @retval Result of the opeartion: USBD_OK if all operations are OK else USBD_FAIL
  */
static int8_t CDC_Itf_Receive(uint8_t* Buf, uint32_t *Len)
{
    uint32_t i=0;
    while (i < *Len) {
        ringbuffer_push(&rx_ringbuffer,Buf[i++]);
    }

    // usb_rx_callback(&rx_ringbuffer);

    USBD_CDC_SetRxBuffer(&USBD_Device, UserRxBuffer);
    USBD_CDC_ReceivePacket(&USBD_Device);

    return (USBD_OK);
}

void CDC_send_packet(void) {
    if (tx_ringbuffer.push_ptr < tx_ringbuffer.pop_ptr) {
        // wraparound
        USBD_CDC_SetTxBuffer(&USBD_Device, tx_ringbuffer.pop_ptr, tx_ringbuffer.data + tx_ringbuffer.sizeof_data - tx_ringbuffer.pop_ptr );
        tx_ringbuffer.pop_ptr = tx_ringbuffer.data;
    } else {
        USBD_CDC_SetTxBuffer(&USBD_Device, tx_ringbuffer.pop_ptr, tx_ringbuffer.push_ptr - tx_ringbuffer.pop_ptr );
        tx_ringbuffer.pop_ptr = tx_ringbuffer.push_ptr;
    }
    USBD_CDC_TransmitPacket(&USBD_Device);

}
// Send data from specified buffer over CDC interface
// input:
//   pBuf - pointer to the data buffer
//   length - size of buffer
uint8_t CDC_Itf_Transmit(uint8_t* pBuf, uint16_t length) {
    uint16_t i = 0;
    while (i<length) {
        ringbuffer_push(&tx_ringbuffer, pBuf[i++]);
    }
    if (!CDC_is_busy) {
        // no transmission in progress, so initiate first Packet
        // all other sub packets will then be handled by the tx_complete callback
        // note that this approach does not use a timer to periodically poll -
        // hence it should be more efficient (no polling if ringbuffer is empty...)
        CDC_send_packet();
        CDC_is_busy = true;
    }
    return 1;
}


/**
  * @}
  */

/**
  * @}
  */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
