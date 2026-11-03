import csv
from typing import List, Tuple

# Archivo donde se guardan las conexiones
ARCHIVO: str = "nodos.csv"


def leer_nombre(mensaje: str) -> str:
    while True:
        # Nombre escrito por el usuario, en mayúsculas para evitar repetidos
        nombre: str = input(mensaje).strip().upper()

        if nombre != "":
            return nombre
        print("El nombre no puede estar vacío.")


def leer_peso(mensaje: str) -> float:
    while True:
        try:
            # Peso escrito por el usuario, falla si no es un número
            peso: float = float(input(mensaje))
        except ValueError:
            print("Escribe un número válido.")
            continue

        if not peso > 0:
            print("El peso debe ser mayor que 0.")
            continue
        return peso


def pedir_conexion() -> Tuple[str, str, float]:
    origen: str = leer_nombre("Nodo origen: ")
    destino: str = leer_nombre("Nodo destino: ")

    while destino == origen:
        print("El destino debe ser distinto del origen.")
        destino = leer_nombre("Nodo destino: ")

    peso: float = leer_peso("Peso: ")
    return origen, destino, peso


def guardar_conexion(conexion: Tuple[str, str, float]) -> bool:
    try:
        # Se abre en modo "a" para agregar sin borrar lo anterior
        with open(ARCHIVO, "a", newline="", encoding="utf-8") as archivo:
            csv.writer(archivo, lineterminator="\n").writerow(conexion)
    except OSError:
        print("No se pudo guardar en el archivo.")
        return False
    return True


def cargar_conexiones() -> List[Tuple[str, str, float]]:
    # Conexiones leídas del archivo
    conexiones: List[Tuple[str, str, float]] = []

    try:
        with open(ARCHIVO, "r", newline="", encoding="utf-8") as archivo:
            for fila in csv.reader(archivo):
                try:
                    conexiones.append((fila[0], fila[1], float(fila[2])))
                except (IndexError, ValueError):
                    # Esto salta el encabezado y las filas dañadas
                    continue
    except FileNotFoundError:
        print("Todavía no existe el archivo nodos.csv.")
    except OSError:
        print("No se pudo leer el archivo.")

    return conexiones
