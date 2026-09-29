# Memoria compartida C — memoria compartida + busy-spin.
#
# -O2 y no -O3: -O3 añade transformaciones agresivas de efecto impredecible sobre un
# bucle dominado por latencia de caché. La medición tiene que ser defendible, no máxima.
# -D_GNU_SOURCE: sin él no compila en Linux/WSL2 (clock_gettime, ftruncate, usleep).
CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -pedantic -D_GNU_SOURCE
LDFLAGS ?=

all: server client

server: server.c common.h ../clasificador.h ../reloj.h
	$(CC) $(CFLAGS) -o $@ server.c $(LDFLAGS)

client: client.c common.h ../clasificador.h ../reloj.h
	$(CC) $(CFLAGS) -o $@ client.c $(LDFLAGS)

clean:
	rm -f server client

.PHONY: all clean
