# Título: Persistencia y validación de conexiones
# Nombre: Dante Tlacaelel Mendoza Alcantar
# Fecha: 16/11/2026
# Descripción: Lee y guarda las conexiones en nodos.csv y valida los datos.
import csv
import os
from typing import List, Tuple

# Archivo donde se guardan las conexiones
ARCHIVO: str = "nodos.csv"


def validar_conexion(
    origen: str, destino: str, peso: str
) -> Tuple[str, str, float]:
    """Limpia y valida los datos; lanza ValueError si algo está mal."""
    # Nombres en mayúsculas para evitar nodos repetidos como "a" y "A"
    origen = origen.strip().upper()
    destino = destino.strip().upper()

    if origen == "" or destino == "":
        raise ValueError("El origen y el destino no pueden estar vacíos.")

    if origen == destino:
        raise ValueError("El destino debe ser distinto del origen.")

    try:
        # Peso convertido a número, falla si el texto no es numérico
        peso_numero: float = float(peso)
    except ValueError:
        raise ValueError("El peso debe ser un número.")

    if not peso_numero > 0:
        raise ValueError("El peso debe ser mayor que 0.")

    return origen, destino, peso_numero


def guardar_conexion(conexion: Tuple[str, str, float]) -> None:
    """Agrega una conexión al final del CSV (puede lanzar OSError)."""
    # Si el archivo no existe todavía, se escribe primero el encabezado
    es_nuevo: bool = not os.path.exists(ARCHIVO)

    # Modo "a" para agregar sin borrar lo anterior
    with open(ARCHIVO, "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        if es_nuevo:
            escritor.writerow(["origen", "destino", "peso"])
        escritor.writerow(conexion)


def cargar_conexiones() -> List[Tuple[str, str, float]]:
    """Lee el CSV; lanza FileNotFoundError si no existe."""
    # Conexiones leídas del archivo
    conexiones: List[Tuple[str, str, float]] = []

    with open(ARCHIVO, "r", newline="", encoding="utf-8") as archivo:
        for fila in csv.reader(archivo):
            try:
                conexiones.append((fila[0], fila[1], float(fila[2])))
            except (IndexError, ValueError):
                # Esto salta el encabezado y las filas dañadas
                continue

    return conexiones