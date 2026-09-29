# -D_GNU_SOURCE: sin él no compila en Linux/WSL2 (clock_gettime de reloj.h).
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
