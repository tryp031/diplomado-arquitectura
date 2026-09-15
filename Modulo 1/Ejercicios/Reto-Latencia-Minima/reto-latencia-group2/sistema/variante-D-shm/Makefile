# Variante D — memoria compartida + busy-spin.
#
# -O2 y no -O3: -O3 habilita transformaciones agresivas (vectorización, desenrollado)
# cuyo efecto sobre un bucle dominado por latencia de caché es impredecible, y que
# harían el resultado más difícil de explicar. La medición tiene que ser defendible,
# no máxima. Si alguien quiere probar -O3, que lo reporte como corrida aparte.
CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -pedantic
LDFLAGS ?=

all: server client

server: server.c common.h ../clasificador.h
	$(CC) $(CFLAGS) -o $@ server.c $(LDFLAGS)

client: client.c common.h ../clasificador.h
	$(CC) $(CFLAGS) -o $@ client.c $(LDFLAGS)

clean:
	rm -f server client

.PHONY: all clean
