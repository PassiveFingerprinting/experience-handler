CC := musl-gcc

CFLAGS := -Wall -Wextra -Wpedantic -std=c11 -Iinclude -O2

SRC := $(shell find src -name "*.c")

TARGET := agent

all: $(TARGET)

$(TARGET):
	$(CC) $(CFLAGS) $(SRC) -static -o $(TARGET)

debug:
	$(CC) $(CFLAGS) -g -O0 $(SRC) -static -o $(TARGET)

strip: $(TARGET)
	strip $(TARGET)

clean:
	rm agent

.PHONY: all clean run debug strip