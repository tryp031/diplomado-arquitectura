CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra
all: micro veredicto
micro: micro.c ../clasificador.h ../reloj.h
	$(CC) $(CFLAGS) -I.. -o $@ micro.c
veredicto: veredicto.c ../clasificador.h ../reloj.h
	$(CC) $(CFLAGS) -I.. -o $@ veredicto.c

clean:
	rm -f micro veredicto
.PHONY: all clean
