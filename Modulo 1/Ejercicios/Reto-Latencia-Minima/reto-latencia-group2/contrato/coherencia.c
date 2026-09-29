/*
 * coherencia.c — ¿clasifican igual la version en C y la version en Python?
 *
 * No mide nada: lee IPs por la entrada estandar y escribe el veredicto de
 * clasificador.h, para que verificar.py lo compare con el de clasificador.py.
 * TCP Python usa clasificador.py y Memoria compartida C usa clasificador.h: comparar
 * sus latencias solo vale si ambas hacen el MISMO trabajo.
 *
 *   cc -O2 -I../sistema -o coherencia coherencia.c
 */
#include "clasificador.h"

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "uso: coherencia <tabla-hosts.csv>  (IPs por entrada estandar)\n");
        return 2;
    }
    if (clasificador_cargar(argv[1]) < 0) return 1;

    char linea[64];
    while (fgets(linea, sizeof linea, stdin)) {
        linea[strcspn(linea, "\r\n")] = '\0';
        if (!linea[0]) continue;
        printf("%s %s\n", linea, nombre_veredicto(clasificar(id_de_ip(linea))));
    }
    return 0;
}
