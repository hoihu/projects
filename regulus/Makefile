UPY_ROOT_DIR=micropython
UPY_PY_DIR = $(UPY_ROOT_DIR)/py

BOARD ?= REGULUS
# If the build directory is not given, make it reflect the board name.
BUILD ?= build-$(BOARD)

include $(UPY_PY_DIR)/mkenv.mk
-include mpconfigport.mk
# include mpconfigboard.mk

# qstr definitions (must come before including py.mk)
QSTR_DEFS = qstrdefsport.h

# include py core make definitions
include $(UPY_PY_DIR)/py.mk


CROSS = 1
CROSS_COMPILE = arm-none-eabi-

CMSIS_DIR=cmsis
CMSIS_INC_DIR= $(CMSIS_DIR)/Include
USB_DIR=cube_usb
USB_CDC_DIR=$(USB_DIR)/cdc
USB_CORE_DIR=$(USB_DIR)/core
CUBE_HAL_DIR = cube_hal

STMHAL_DIR = $(UPY_ROOT_DIR)/stmhal

DFU= $(UPY_ROOT_DIR)/tools/dfu.py
PYDFU = $(UPY_ROOT_DIR)/tools/pydfu.py
DFU_UTIL ?= dfu-util
DEVICE=0483:df11

#regulus
INC =  -I.
INC += -I$(BUILD)
INC += -I$(CMSIS_INC_DIR)
INC += -I$(CMSIS_DIR)
INC += -I$(USB_DIR)
INC += -I$(CUBE_HAL_DIR)/Inc
INC += -I$(USB_CDC_DIR)
INC += -I$(USB_CORE_DIR)

#upy staff
INC += -I$(UPY_ROOT_DIR)
INC += -I$(STMHAL_DIR)
INC += -I$(UPY_PY_DIR)
INC += -I$(UPY_ROOT_DIR)/lib/mp-readline

CFLAGS  = $(INC) -Wall -Wpointer-arith -Werror -ansi -std=gnu99 -nostdlib -DSTM32L151xC
CFLAGS  += -DSTM32_HAL_H='<stm32l1xx_hal.h>'
CFLAGS  += -mthumb -mabi=aapcs-linux -mfpu=fpv4-sp-d16 -fsingle-precision-constant -Wdouble-promotion
CFLAGS  += -mtune=cortex-m3 -mcpu=cortex-m3 -mfloat-abi=soft
CFLAGS  += -fdata-sections -ffunction-sections
COPT += -Os -DNDEBUG

LDSCRIPT = stm32l151.ld
LDFLAGS = -T$(LDSCRIPT) -nostdlib
LDFLAGS += --gc-sections -Map=$@.map


SRC_S = \
	$(wildcard ./*.s) \


SRC_C = \
	$(wildcard $(CMSIS_DIR)/*.c) \
	$(wildcard $(CUBE_HAL_DIR)/Src/*.c) \
	$(wildcard $(USB_CDC_DIR)/*.c) \
	$(wildcard $(USB_CORE_DIR)/*.c) \
	$(wildcard $(USB_DIR)/*.c) \
	$(wildcard ./*.c) \

STM_SRC_C = \
	$(STMHAL_DIR)/printf.c \
	$(STMHAL_DIR)/pyexec.c \
	$(STMHAL_DIR)/gccollect.c \
	$(UPY_ROOT_DIR)/lib/libc/string0.c \
	$(UPY_ROOT_DIR)/lib/mp-readline/readline.c \

OBJ =
OBJ += $(PY_O)
OBJ += $(addprefix $(BUILD)/, $(SRC_C:.c=.o))
OBJ += $(addprefix $(BUILD)/, $(SRC_S:.s=.o))
OBJ += $(addprefix $(BUILD)/, $(STM_SRC_C:.c=.o))


all: $(BUILD)/firmware.dfu $(BUILD)/firmware.hex

.PHONY: download

$(BUILD)/firmware.dfu: $(BUILD)/firmware.bin
	$(ECHO) "Create $@"
	$(PYTHON) $(DFU) -b 0x08000000:./$(BUILD)/firmware.bin $@

$(BUILD)/firmware.hex: $(BUILD)/firmware.elf
	$(ECHO) "Create $@"
	$(Q)$(OBJCOPY) -O ihex $< $@

$(BUILD)/firmware.bin: $(BUILD)/firmware.elf
	$(Q)$(OBJCOPY) -O binary $< $@

$(BUILD)/firmware.elf: $(OBJ)
	$(ECHO) "LINK $@"
	$(Q)$(LD) $(LDFLAGS) -o $@ $(OBJ) $(LIBS)
	$(Q)$(SIZE) $@

download: $(BUILD)/firmware.dfu
	$(DFU_UTIL) -a 0 -d $(DEVICE) -s 0x08000000 -D $(BUILD)/firmware.bin

debug:
	@echo $(SOURCES)


include $(UPY_PY_DIR)/mkrules.mk
