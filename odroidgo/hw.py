from machine import Pin, ADC, PWM
import display

# Display
tft = display.TFT()
tft.init(tft.ILI9341, width=240, height=320, 
        backl_pin=14, 
        miso=19, 
        mosi=23, 
        clk=18, 
        cs=5, 
        dc=21, 
        bgr=True, backl_on=0, invrot=0, rot=tft.LANDSCAPE_FLIP)
tft.font(tft.FONT_DejaVu24)

# LED 
led_blue = Pin(2, mode=Pin.OUT)

# buttons, joystick
button_a = Pin(32, mode=Pin.IN, pull=Pin.PULL_UP)
button_b = Pin(33, mode=Pin.IN, pull=Pin.PULL_UP)

button_menu   = Pin(13, mode=Pin.IN, pull=Pin.PULL_UP)
button_select = Pin(27, mode=Pin.IN, pull=Pin.PULL_UP)
button_volume = Pin(0, mode=Pin.IN)
button_start  = Pin(39, mode=Pin.IN)

# 3 joysticks states are mapped with analog voltages
# needs ADCs, configured to read from 3V
joy_x = ADC(34)
joy_x.atten(joy_x.ATTN_11DB)

joy_y = ADC(35)
joy_y.atten(joy_y.ATTN_11DB)

def joy_get_state(joy_pin): 
    adcv = joy_pin.read()
    if adcv > 2000: return 2
    if adcv > 1000: return 1
    return 0

# speaker
speaker_pwm = PWM(26, freq=1000, duty=0.5)
speaker_driver_enable = Pin(25, mode=Pin.OUT)
speaker_driver_enable.value(0)


    