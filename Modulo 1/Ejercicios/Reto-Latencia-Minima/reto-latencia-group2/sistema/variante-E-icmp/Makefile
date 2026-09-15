CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra
all: client
client: client.c ../reloj.h ../clasificador.h
	$(CC) $(CFLAGS) -o $@ client.c
clean:
	rm -f client
.PHONY: all clean
