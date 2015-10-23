
CMSIS_DIR=cmsis
CDC_DIR=cdc
CMSIS_BOOT_DIR=cmsis_boot
CMSIS_LIB_DIR=cmsis_lib
USBDEV_DIR=usbd

DFU= dfu.py
PYDFU = pydfu.py
DFU_UTIL ?= dfu-util
DEVICE=0483:df11

BUILDDIR = build
CMSIS_DIR=cmsis
CMSIS_BOOT_DIR=cmsis_boot
CMSIS_LIB_DIR=cmsis_lib
USB_DEV_DIR=usbd

SOURCES = \
	$(wildcard $(CMSIS_BOOT_DIR)/*.c) \
	$(wildcard $(CMSIS_BOOT_DIR)/Startup/*.c) \
	$(wildcard $(CMSIS_LIB_DIR)/Source/*.c) \
	$(wildcard $(USB_DEV_DIR)/*.c) \
	$(wildcard cdc/*.c) \
	usb_ll.c \
	main.c

OBJECTS = $(addprefix $(BUILDDIR)/, $(addsuffix .o, $(basename $(SOURCES))))

INC =  -I.
INC += -I$(BUILDDIR)
INC += -Icdc
INC += -I$(CMSIS_LIB_DIR)/include
INC += -I$(CMSIS_DIR)
INC += -I$(CMSIS_BOOT_DIR)
INC += -I$(USBDEV_DIR)

ELF = $(BUILDDIR)/program.elf
HEX = $(BUILDDIR)/program.hex
BIN = $(BUILDDIR)/program.bin

CC = arm-none-eabi-gcc
LD = arm-none-eabi-gcc
AR = arm-none-eabi-ar
OBJCOPY = arm-none-eabi-objcopy

CFLAGS  = $(INC) -Wall -Wpointer-arith -Werror -ansi -std=gnu99 -nostdlib
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
