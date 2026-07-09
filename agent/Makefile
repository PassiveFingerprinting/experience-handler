CC := musl-gcc

CFLAGS := -Wall -Wextra -Wpedantic -std=c11 -Iinclude -O2 -static

SRC := $(shell find src -name "*.c")
OBJ := $(SRC:.c=.o)

TARGET := agent

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(OBJ) $(CFLAGS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

debug: CFLAGS += -g -O0
debug: clean $(TARGET)

strip: $(TARGET)
	strip $(TARGET)

clean:
	rm -f $(OBJ) $(TARGET)

.PHONY: all clean debug strip