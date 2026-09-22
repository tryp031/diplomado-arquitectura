# -D_GNU_SOURCE: sin él, en Linux/WSL2 no compila: bajo -std=c11 la biblioteca C deja sin
# declarar clock_gettime (usado por reloj.h). No cambia el nivel de optimización.
# Mismo diagnóstico y mismo fix que variante-D-shm/Makefile.
CC      ?= cc
CFLAGS  ?= -std=c11 -O2 -Wall -Wextra -D_GNU_SOURCE
all: micro veredicto
micro: micro.c ../clasificador.h ../reloj.h
	$(CC) $(CFLAGS) -I.. -o $@ micro.c
veredicto: veredicto.c ../clasificador.h ../reloj.h
	$(CC) $(CFLAGS) -I.. -o $@ veredicto.c

clean:
	rm -f micro veredicto
.PHONY: all clean
