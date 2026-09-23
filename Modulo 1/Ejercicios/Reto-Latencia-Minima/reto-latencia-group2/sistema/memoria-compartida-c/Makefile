# Memoria compartida C — memoria compartida + busy-spin.
#
# -O2 y no -O3: -O3 habilita transformaciones agresivas (vectorización, desenrollado)
# cuyo efecto sobre un bucle dominado por latencia de caché es impredecible, y que
# harían el resultado más difícil de explicar. La medición tiene que ser defendible,
# no máxima. Si alguien quiere probar -O3, que lo reporte como corrida aparte.
#
# -D_GNU_SOURCE: sin él, en Linux/WSL2 no compila: bajo -std=c11 la biblioteca C deja sin
# declarar clock_gettime, ftruncate y usleep. No cambia el nivel de optimización.
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
