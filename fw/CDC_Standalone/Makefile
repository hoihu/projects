
CMSIS_DIR=cmsis
CMSIS_SOURCE_DIR=cmsis
USBDEV_DIR=cube_usb
USB_CORE_DIR = $(USBDEV_DIR)/core
USB_CDC_DIR = $(USBDEV_DIR)/cdc
CUBE_HAL_DIR = cube_hal

DFU= dfu.py
PYDFU = pydfu.py
DFU_UTIL ?= dfu-util
DEVICE=0483:df11

BUILDDIR = build

SOURCES = \
	$(wildcard $(CMSIS_DIR)/*.c) \
	$(wildcard $(CUBE_HAL_DIR)/Src/*.c) \
	$(wildcard $(USB_CDC_DIR)/*.c) \
	$(wildcard $(USB_CORE_DIR)/*.c) \
	$(wildcard ./*.c) \

OBJECTS = $(addprefix $(BUILDDIR)/, $(addsuffix .o, $(basename $(SOURCES))))

INC =  -I.
INC += -I$(BUILDDIR)
INC += -I$(USB_CDC_DIR)
INC += -I$(USB_CORE_DIR)
INC += -I$(CUBE_HAL_DIR)/Inc
INC += -I$(CMSIS_DIR)/Include
INC += -Icmsis

ELF = $(BUILDDIR)/program.elf
HEX = $(BUILDDIR)/program.hex
BIN = $(BUILDDIR)/program.bin

CC = arm-none-eabi-gcc
LD = arm-none-eabi-gcc
AR = arm-none-eabi-ar
OBJCOPY = arm-none-eabi-objcopy

CFLAGS  = $(INC) -Wall -Wpointer-arith -Werror -ansi -std=gnu99 -nostdlib -DSTM32L151xC
CFLAGS  += -mthumb -mabi=aapcs-linux -mfpu=fpv4-sp-d16 -fsingle-precision-constant -Wdouble-promotion
CFLAGS  += -mtune=cortex-m3 -mcpu=cortex-m3 -mfloat-abi=soft -DMCU_SERIES_L1
CFLAGS  += -fdata-sections -ffunction-sections


LDSCRIPT = stm32l151.ld
LDFLAGS = -T$(LDSCRIPT) -mthumb -mcpu=cortex-m3 -nostdlib
LDFLAGS += -Wl,--gc-sections -Wl,-Map=$@.map

$(BIN): $(ELF)
	$(OBJCOPY) -O binary $< $@

$(HEX): $(ELF)
	$(OBJCOPY) -O ihex $< $@

$(ELF): $(OBJECTS)
	$(LD) $(LDFLAGS) -o $@ $(OBJECTS) $(LDLIBS)

$(BUILDDIR)/%.o: %.c
	mkdir -p $(dir $@)
	$(CC) -c $(CFLAGS) $< -o $@

$(BUILDDIR)/%.o: %.s
	mkdir -p $(dir $@)
	$(CC) -c $(CFLAGS) $< -o $@

flash: $(BIN)
	st-flash write $(BIN) 0x8000000

clean:
	rm -rf build

download:
	$(DFU_UTIL) -a 0 -d $(DEVICE) -s 0x08000000 -D $(BIN)


debug:
	@echo $(SOURCES)
