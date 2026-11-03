from typing import List, Tuple

import iohandle
from grafo import Grafo


def construir_grafo(conexiones: List[Tuple[str, str, float]]) -> Grafo:
    # Grafo en memoria que se llena con lo que hay en el CSV
    grafo: Grafo = Grafo()

    for origen, destino, peso in conexiones:
        for nombre in (origen, destino):
            if nombre not in grafo.nodos:
                grafo.agregar_nodo(nombre)
        grafo.agregar_conexion(origen, destino, peso)

    return grafo


def agregar_conexion() -> None:
    if iohandle.guardar_conexion(iohandle.pedir_conexion()):
        print("Conexión guardada.")


def calcular_ruta() -> None:
    grafo: Grafo = construir_grafo(iohandle.cargar_conexiones())

    if len(grafo.nodos) == 0:
        print("No hay conexiones, agrega alguna primero.")
        return

    print("Nodos:", ", ".join(sorted(grafo.nodos)))
    origen: str = iohandle.leer_nombre("Nodo origen: ")
    destino: str = iohandle.leer_nombre("Nodo destino: ")

    if origen not in grafo.nodos or destino not in grafo.nodos:
        print("Alguno de los nodos no existe.")
        return

    costo, ruta = grafo.dijkstra(origen, destino)

    if len(ruta) == 0:
        print("No hay camino entre esos nodos.")
    else:
        print("Costo total:", costo)
        print("Ruta:", " -> ".join(ruta))


def main() -> None:
    while True:
        print("\n1. Agregar conexión")
        print("2. Calcular ruta")
        print("3. Salir")

        # Opción elegida en el menú
        opcion: str = input("Opción: ").strip()

        if opcion == "1":
            agregar_conexion()
        elif opcion == "2":
            calcular_ruta()
        elif opcion == "3":
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma terminado.")
