# Título: Interfaz web de rutas con Streamlit
# Autor: Dante Tlacaelel Mendoza Alcantar
# Fecha: 16/11/2026
# Descripción: Frontend Streamlit para registrar conexiones y usar Dijkstra.
import pandas as pd
import streamlit as st

import io_handler
from grafo import Grafo, construir_grafo


def cargar_grafo_una_vez() -> None:
    """Lee el CSV solo la primera vez y deja el grafo en session_state."""
    if "grafo" in st.session_state:
        return

    # Conexiones del CSV; queda vacía si el archivo no se pudo leer
    conexiones = []

    try:
        conexiones = io_handler.cargar_conexiones()
    except FileNotFoundError:
        st.warning("No existe nodos.csv, se inicia con una red vacía.")
    except PermissionError:
        st.error("No hay permiso para leer nodos.csv.")

    st.session_state["grafo"] = construir_grafo(conexiones)


def mostrar_calculador(grafo: Grafo) -> None:
    st.subheader("Calcular ruta más corta")

    col_origen, col_destino = st.columns(2)
    origen: str = col_origen.text_input("Nodo origen").strip().upper()
    destino: str = col_destino.text_input("Nodo destino").strip().upper()

    if not st.button("Calcular ruta"):
        return

    if origen == "" or destino == "":
        st.warning("Escribe el nodo origen y el nodo destino.")
    elif origen not in grafo.nodos or destino not in grafo.nodos:
        st.error("Alguno de los nodos no existe en la red.")
    else:
        costo, ruta = grafo.dijkstra(origen, destino)

        if len(ruta) == 0:
            st.warning(f"No existe una ruta entre {origen} y {destino}.")
        else:
            st.success(f"Costo total mínimo: {costo}")
            st.write("Recorrido: " + " → ".join(ruta))


def mostrar_registro(grafo: Grafo) -> None:
    st.subheader("Registrar nueva conexión")

    with st.form("form_conexion", clear_on_submit=True):
        origen: str = st.text_input("Nodo origen")
        destino: str = st.text_input("Nodo destino")
        peso: str = st.text_input("Peso")
        enviado: bool = st.form_submit_button("Guardar conexión")

    if not enviado:
        return

    try:
        origen, destino, peso_numero = io_handler.validar_conexion(
            origen, destino, peso
        )
        io_handler.guardar_conexion((origen, destino, peso_numero))
    except ValueError as error:
        st.error(str(error))
    except PermissionError:
        st.error("No hay permiso para escribir en nodos.csv.")
    except OSError:
        st.error("No se pudo guardar en nodos.csv.")
    else:
        # Solo si se guardó en disco, se actualiza el grafo en memoria
        for nombre in (origen, destino):
            if nombre not in grafo.nodos:
                grafo.agregar_nodo(nombre)
        grafo.agregar_conexion(origen, destino, peso_numero)
        st.success(f"Conexión {origen} - {destino} guardada.")


def mostrar_red(grafo: Grafo) -> None:
    st.subheader("Red actual")

    # Filas de la tabla; cada conexión se agrega una sola vez
    filas = []

    for nombre, nodo in grafo.nodos.items():
        for vecino, peso in nodo.vecinos.items():
            if nombre < vecino:
                filas.append(
                    {"Origen": nombre, "Destino": vecino, "Peso": peso}
                )

    if len(filas) == 0:
        st.info("La red está vacía.")
    else:
        st.dataframe(pd.DataFrame(filas))


def main() -> None:
    st.title("Rutas óptimas con Dijkstra")

    cargar_grafo_una_vez()

    # Grafo guardado en memoria durante toda la sesión
    grafo: Grafo = st.session_state["grafo"]

    tab_calculo, tab_registro, tab_red = st.tabs(
        ["Calculador", "Registro", "Visor de red"]
    )

    with tab_calculo:
        mostrar_calculador(grafo)
    with tab_registro:
        mostrar_registro(grafo)
    with tab_red:
        mostrar_red(grafo)


main()
