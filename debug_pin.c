#define DEBUG_PIN                         GPIO_PIN_0
#define DEBUG_GPIO_PORT                   GPIOA
#define DEBUG_GPIO_CLK_ENABLE()           __GPIOA_CLK_ENABLE()
#define DEBUG_GPIO_CLK_DISABLE()          __GPIOA_CLK_DISABLE()

void init_debug_pin(void) {
    GPIO_InitTypeDef  gpioinitstruct = {0};
    /* Enable the GPIO Clock */
    DEBUG_GPIO_CLK_ENABLE();

    /* Configure the USB D+ pin */
    gpioinitstruct.Pin    = DEBUG_PIN;
    gpioinitstruct.Mode   = GPIO_MODE_OUTPUT_PP;
    gpioinitstruct.Pull   = GPIO_NOPULL;
    gpioinitstruct.Speed  = GPIO_SPEED_LOW;
    HAL_GPIO_Init(DEBUG_GPIO_PORT, &gpioinitstruct);
}

void toogle_debug(void) {
    HAL_GPIO_WritePin(DEBUG_GPIO_PORT, DEBUG_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(DEBUG_GPIO_PORT, DEBUG_PIN, GPIO_PIN_RESET);
}
