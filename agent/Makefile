CC := musl-gcc

CFLAGS := -Wall -Wextra -Wpedantic -std=c11 -Iinclude -O2

SRC := $(shell find src -name "*.c")

TARGET := agent

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -static -o $(TARGET)

debug:
	$(CC) $(CFLAGS) -g -O0 $(SRC) -static -o $(TARGET)

strip: $(TARGET)
	strip $(TARGET)

clean:
	rm -f agent
	rm -f src/*.o

.PHONY: all clean debug strip