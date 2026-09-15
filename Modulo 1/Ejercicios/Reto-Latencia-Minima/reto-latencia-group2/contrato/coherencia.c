/*
 * coherencia.c — ¿clasifican igual la version en C y la version en Python?
 *
 * No mide nada y no forma parte del sistema: es una herramienta del contrato de
 * trabajo. Lee IPs por la entrada estandar y escribe el veredicto que da
 * clasificador.h, para que verificar.py compare esa salida con la de
 * clasificador.py sobre las mismas entradas.
 *
 * Por que importa: `control-Bc-tcp-c` existe para AISLAR el efecto del lenguaje,
 * manteniendo todo lo demas igual. Si los dos clasificadores dejan de coincidir,
 * B y Bc pasan a hacer trabajos distintos y el control deja de controlar nada
 * —sin que ningun test falle y sin que nadie se entere—. Esta comprobacion es
 * barata y cierra ese agujero.
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
