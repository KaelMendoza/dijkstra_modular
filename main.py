# Título: Dijkstra en consola
# Autor: Dante Tlacaelel Mendoza Alcantar
# Fecha: 16/11/2026
# Descripción: Menú de consola para agregar conexiones y calcular rutas.
import io_handler
from grafo import Grafo, construir_grafo


def agregar_conexion() -> None:
    while True:
        origen: str = input("Nodo origen: ")
        destino: str = input("Nodo destino: ")
        peso: str = input("Peso: ")

        try:
            conexion = io_handler.validar_conexion(origen, destino, peso)
            io_handler.guardar_conexion(conexion)
        except ValueError as error:
            print("Error:", error)
            continue
        except OSError:
            print("No se pudo guardar en el archivo.")
        break

    print("Conexión guardada.")


def calcular_ruta() -> None:
    try:
        grafo: Grafo = construir_grafo(io_handler.cargar_conexiones())
    except FileNotFoundError:
        print("Todavía no existe el archivo nodos.csv.")
        return

    print("Nodos:", ", ".join(sorted(grafo.nodos)))
    origen: str = input("Nodo origen: ").strip().upper()
    destino: str = input("Nodo destino: ").strip().upper()

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