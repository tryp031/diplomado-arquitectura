CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -pedantic

all: server client
server: server.c ../reloj.h ../clasificador.h
	$(CC) $(CFLAGS) -o $@ server.c
client: client.c ../reloj.h ../clasificador.h
	$(CC) $(CFLAGS) -o $@ client.c
clean:
	rm -f server client
.PHONY: all clean
