# Título: Calculadora de nodos con Streamlit
# Autor: Dante Tlacaelel Mendoza Alcantar
# Fecha: 16/11/2026
# Descripción: App web con mapa del grafo clicable, tabla y Dijkstra.
import html
import math
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import io_handler
from grafo import Grafo, construir_grafo

# Tipo para guardar la posición (x, y) de cada nodo en el mapa
Posiciones = Dict[str, Tuple[float, float]]

# Paleta: negro y naranja, con un naranja claro y un texto crema
NARANJA: str = "#FF6A00"
NARANJA_CLARO: str = "#FFB066"
CREMA: str = "#FFE2C2"
NEGRO: str = "#000000"

# Estilos CSS: fondo negro total y un mismo diseño para todos los elementos
ESTILOS: str = """
<style>
:root {
  --naranja: #FF6A00;
  --claro: #FFB066;
  --texto: #FFE2C2;
  --borde: #3D1D00;
}
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stHeader"],
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
  background: #000 !important;
  color: var(--texto);
  font-family: "Segoe UI", system-ui, sans-serif;
}
[data-testid="stToolbar"], [data-testid="stDecoration"], footer {
  display: none !important;
}
.block-container { padding-top: 4rem; }
[data-testid="stSidebar"] { border-right: 1px solid var(--borde); }
h1 {
  color: var(--naranja) !important;
  font-weight: 600;
  letter-spacing: .5px;
}
h2, h3 { color: var(--texto) !important; font-weight: 600; }
p, label, span, li { color: var(--texto); }
[data-testid="stCaptionContainer"] p { color: var(--claro); opacity: .8; }
[data-testid="stWidgetLabel"] p { color: var(--claro); font-size: .85rem; }
.stTextInput div[data-baseweb="input"],
.stTextInput div[data-baseweb="base-input"] {
  background: #000 !important;
  border-radius: 8px;
}
.stTextInput div[data-baseweb="input"] {
  border: 1px solid var(--borde);
  transition: all .15s ease;
}
.stTextInput div[data-baseweb="input"]:focus-within {
  border-color: var(--naranja);
  box-shadow: 0 0 10px rgba(255, 106, 0, .35);
}
.stTextInput input { color: var(--texto); background: #000 !important; }
[data-testid="stForm"] {
  background: #000;
  border: 1px solid var(--borde);
  border-radius: 8px;
}
.stButton button, [data-testid="stFormSubmitButton"] button {
  background: #000;
  color: var(--naranja);
  font-weight: 600;
  border: 1px solid var(--naranja);
  border-radius: 8px;
  transition: all .15s ease;
}
.stButton button:hover,
[data-testid="stFormSubmitButton"] button:hover {
  background: var(--naranja);
  color: #000;
  box-shadow: 0 0 16px rgba(255, 106, 0, .55);
}
[data-testid="stAlert"], [data-testid="stAlertContainer"] {
  background: #000 !important;
  color: var(--texto);
  border: 1px solid var(--borde);
  border-left: 3px solid var(--naranja);
  border-radius: 8px;
}
[data-testid="stAlert"] > div { background: transparent !important; }
[data-testid="stAlert"] p { color: var(--texto); }
[data-testid="stExpander"] {
  background: #000;
  border: 1px solid var(--borde);
  border-radius: 8px;
}
[data-testid="stExpander"] details, [data-testid="stExpander"] summary {
  background: #000;
  color: var(--texto);
}
[data-testid="stPlotlyChart"] {
  background: #000;
  border: 1px solid var(--borde);
  border-radius: 8px;
}
[data-testid="stMetricLabel"] p { color: var(--claro); }
[data-testid="stMetricValue"] { color: var(--naranja); }
[data-testid="stTable"] table { width: 100%; border-collapse: collapse; }
[data-testid="stTable"] th {
  background: #000;
  color: var(--claro);
  border-bottom: 1px solid var(--naranja);
}
[data-testid="stTable"] td {
  background: #000;
  color: var(--texto);
  border-bottom: 1px solid var(--borde);
}
@keyframes aparecer {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
.nodo-ruta {
  display: inline-block;
  margin: 3px 0;
  padding: 4px 14px;
  color: var(--texto);
  font-weight: 600;
  background: #000;
  border: 1px solid var(--naranja);
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(255, 106, 0, .35);
  animation: aparecer .35s ease both;
}
.flecha-ruta { color: var(--naranja); padding: 0 6px; }
</style>
"""


def posicion_inicial(indice: int) -> Tuple[float, float]:
    """Punto de partida en espiral para el nodo número "indice"."""
    # Distancia al centro y ángulo (ángulo áureo) del punto
    radio: float = 1.2 * math.sqrt(indice + 0.5)
    angulo: float = indice * 2.39996
    return radio * math.cos(angulo), radio * math.sin(angulo)


def acomodar_nodos(grafo: Grafo, posiciones: Posiciones) -> None:
    """Coloca los nodos nuevos; los que ya estaban no se mueven."""
    # Nodos sin posición (todos, la primera vez que se dibuja el mapa)
    nuevos: List[str] = [n for n in grafo.nodos if n not in posiciones]

    if len(nuevos) == 0:
        return

    for nombre in nuevos:
        posiciones[nombre] = posicion_inicial(len(posiciones))

    # Distancia ideal entre nodos conectados
    ideal: float = 1.8

    # Pasos de relajación: los nodos se repelen y los conectados se atraen
    pasos: int = 200

    for paso in range(pasos):
        # Cuánto puede moverse un nodo en este paso; baja con el tiempo
        temperatura: float = 0.6 * (1 - paso / pasos)
        fuerzas: Dict[str, List[float]] = {n: [0.0, 0.0] for n in nuevos}

        for nombre in nuevos:
            x, y = posiciones[nombre]

            # Repulsión contra todos los demás nodos
            for otro, (ox, oy) in posiciones.items():
                if otro != nombre:
                    dx, dy = x - ox, y - oy
                    distancia = max(math.hypot(dx, dy), 0.01)
                    fuerza = ideal * ideal / distancia
                    fuerzas[nombre][0] += dx / distancia * fuerza
                    fuerzas[nombre][1] += dy / distancia * fuerza

            # Atracción hacia sus vecinos
            for vecino in grafo.nodos[nombre].vecinos:
                dx, dy = posiciones[vecino][0] - x, posiciones[vecino][1] - y
                distancia = max(math.hypot(dx, dy), 0.01)
                fuerza = distancia * distancia / ideal
                fuerzas[nombre][0] += dx / distancia * fuerza
                fuerzas[nombre][1] += dy / distancia * fuerza

            # Una fuerza leve hacia el centro evita que se alejen mucho
            fuerzas[nombre][0] -= 0.4 * x
            fuerzas[nombre][1] -= 0.4 * y

        for nombre in nuevos:
            fx, fy = fuerzas[nombre]
            largo = max(math.hypot(fx, fy), 0.01)
            avance = min(largo, temperatura)
            x, y = posiciones[nombre]
            posiciones[nombre] = (x + fx / largo * avance,
                                  y + fy / largo * avance)


def lista_aristas(grafo: Grafo) -> List[Tuple[str, str, float]]:
    # Cada conexión aparece una sola vez (A-B y no también B-A)
    aristas: List[Tuple[str, str, float]] = []

    for nombre, nodo in grafo.nodos.items():
        for vecino, peso in nodo.vecinos.items():
            if nombre < vecino:
                aristas.append((nombre, vecino, peso))

    return aristas


def punto_medio(
    posiciones: Posiciones, a: str, b: str
) -> Tuple[float, float]:
    xa, ya = posiciones[a]
    xb, yb = posiciones[b]
    return (xa + xb) / 2, (ya + yb) / 2


def cargar_grafo_una_vez() -> None:
    """Lee el CSV solo la primera vez y deja el grafo en session_state."""
    if "grafo" in st.session_state:
        return

    # Conexiones del CSV; queda vacía si el archivo no se pudo leer
    conexiones = []

    try:
        conexiones = io_handler.cargar_conexiones()
    except FileNotFoundError:
        st.warning("No se encontró nodos.csv, se inicia con un mapa vacío.")
    except PermissionError:
        st.error("No hay permiso para leer nodos.csv.")

    st.session_state["grafo"] = construir_grafo(conexiones)


def iniciar_estado() -> None:
    # Valores iniciales de lo que se recuerda entre interacciones
    st.session_state.setdefault("origen_calc", "")
    st.session_state.setdefault("destino_calc", "")
    st.session_state.setdefault("posiciones", {})
    st.session_state.setdefault("version_mapa", 0)
    st.session_state.setdefault("nueva_arista", None)


def elegir_nodo(nombre: str) -> None:
    """Primer toque = origen, segundo = destino, tercero = reinicia."""
    origen: str = st.session_state["origen_calc"].strip().upper()
    destino: str = st.session_state["destino_calc"].strip().upper()

    if origen == "":
        st.session_state["origen_calc"] = nombre
    elif destino == "" and nombre != origen:
        st.session_state["destino_calc"] = nombre
    else:
        st.session_state["origen_calc"] = nombre
        st.session_state["destino_calc"] = ""


def al_tocar_mapa() -> None:
    """Se ejecuta al tocar el mapa: elige un nodo o una conexión."""
    # Cada toque cambia la llave del mapa para borrar la selección vieja
    clave: str = f"mapa_{st.session_state['version_mapa']}"
    st.session_state["version_mapa"] += 1
    st.session_state["nueva_arista"] = None

    try:
        punto = st.session_state[clave]["selection"]["points"][-1]
        x: float = punto["x"]
        y: float = punto["y"]
    except (KeyError, IndexError, TypeError):
        return

    grafo: Grafo = st.session_state["grafo"]
    posiciones: Posiciones = st.session_state["posiciones"]

    # Primero se busca si el toque fue sobre un nodo
    for nombre, (px, py) in posiciones.items():
        if abs(px - x) < 1e-3 and abs(py - y) < 1e-3:
            elegir_nodo(nombre)
            return

    # Si no, se busca si fue sobre el rombo de una conexión
    for origen, destino, _ in lista_aristas(grafo):
        mx, my = punto_medio(posiciones, origen, destino)
        if abs(mx - x) < 1e-3 and abs(my - y) < 1e-3:
            st.session_state["origen_calc"] = origen
            st.session_state["destino_calc"] = destino
            return


def limpiar_seleccion() -> None:
    st.session_state["origen_calc"] = ""
    st.session_state["destino_calc"] = ""
    st.session_state["nueva_arista"] = None


def buscar_recorrido(
    grafo: Grafo, origen: str, destino: str
) -> Tuple[float, List[str]]:
    # Solo se calcula si los dos nodos existen y son distintos
    if origen == destino:
        return float("inf"), []
    if origen not in grafo.nodos or destino not in grafo.nodos:
        return float("inf"), []

    return grafo.dijkstra(origen, destino)


def lineas_de_pares(
    posiciones: Posiciones, pares: List[Tuple[str, str]]
) -> Tuple[List[Optional[float]], List[Optional[float]]]:
    # Una sola línea con huecos (None) para dibujar varias conexiones
    xs: List[Optional[float]] = []
    ys: List[Optional[float]] = []

    for a, b in pares:
        xs += [posiciones[a][0], posiciones[b][0], None]
        ys += [posiciones[a][1], posiciones[b][1], None]

    return xs, ys


def agregar_lineas(
    figura: go.Figure,
    posiciones: Posiciones,
    pares: List[Tuple[str, str]],
    capas: Tuple[Tuple[int, float, str, str], ...],
) -> None:
    # Cada capa es (grosor, opacidad, color, estilo de línea)
    xs, ys = lineas_de_pares(posiciones, pares)

    for ancho, opacidad, color, estilo in capas:
        figura.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                line={"width": ancho, "color": color, "dash": estilo},
                opacity=opacidad,
                hoverinfo="skip",
            )
        )


def colores_de_nodo(
    nombre: str, origen: str, destino: str, ruta: List[str]
) -> Tuple[str, str, str]:
    """Devuelve (relleno, borde, color del texto) según el papel del nodo."""
    if nombre == origen:
        return NARANJA, NARANJA, NEGRO
    if nombre == destino:
        return NARANJA_CLARO, NARANJA_CLARO, NEGRO
    if nombre in ruta:
        return NEGRO, NARANJA_CLARO, CREMA
    return NEGRO, NARANJA, CREMA


def construir_figura(
    grafo: Grafo,
    posiciones: Posiciones,
    origen: str,
    destino: str,
    ruta: List[str],
) -> go.Figure:
    figura: go.Figure = go.Figure()
    aristas: List[Tuple[str, str, float]] = lista_aristas(grafo)
    nombres: List[str] = list(grafo.nodos)

    # Conexiones normales, finas y tenues
    pares: List[Tuple[str, str]] = [(a, b) for a, b, _ in aristas]
    agregar_lineas(figura, posiciones, pares, ((2, 0.45, NARANJA, "solid"),))

    # Última conexión agregada, resaltada hasta el siguiente toque
    nueva = st.session_state["nueva_arista"]
    if nueva is not None and nueva[0] in grafo.nodos:
        agregar_lineas(
            figura, posiciones, [nueva],
            ((3, 1.0, NARANJA_CLARO, "dot"),),
        )

    # Recorrido encontrado: línea clara con un halo suave
    if len(ruta) > 1:
        agregar_lineas(
            figura, posiciones, list(zip(ruta, ruta[1:])),
            ((12, 0.18, NARANJA, "solid"), (3, 1.0, NARANJA_CLARO, "solid")),
        )

    # Rombos con el peso en medio de cada conexión (se pueden tocar)
    medios = [punto_medio(posiciones, a, b) for a, b, _ in aristas]
    figura.add_trace(
        go.Scatter(
            x=[m[0] for m in medios],
            y=[m[1] for m in medios],
            mode="markers+text",
            text=[f"{peso:g}" for _, _, peso in aristas],
            textposition="top center",
            textfont={"color": NARANJA_CLARO, "size": 12},
            marker={
                "size": 10,
                "symbol": "diamond",
                "color": NEGRO,
                "line": {"color": NARANJA, "width": 1.5},
            },
            hovertext=[f"{a} - {b}: clic para elegir" for a, b, _ in aristas],
            hoverinfo="text",
            unselected={"marker": {"opacity": 1}},
        )
    )

    # Colores de cada nodo según su papel en el recorrido
    estilos = [colores_de_nodo(n, origen, destino, ruta) for n in nombres]
    xs: List[float] = [posiciones[n][0] for n in nombres]
    ys: List[float] = [posiciones[n][1] for n in nombres]

    # Halo suave solo detrás de los nodos del recorrido
    halo = [20 if n in ruta else 0 for n in nombres]
    figura.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker={"size": [34 + h * 2 for h in halo], "color": NARANJA},
            opacity=0.0 if len(ruta) == 0 else 0.18,
            hoverinfo="skip",
        )
    )

    # Nodos (se pueden tocar)
    figura.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            text=nombres,
            textfont={
                "size": 15,
                "family": "Segoe UI, sans-serif",
                "color": [e[2] for e in estilos],
            },
            marker={
                "size": 34,
                "color": [e[0] for e in estilos],
                "line": {"color": [e[1] for e in estilos], "width": 2},
            },
            hovertext=[f"Nodo {n}: clic para elegirlo" for n in nombres],
            hoverinfo="text",
            unselected={"marker": {"opacity": 1}},
        )
    )

    # Límites del mapa: se ajustan a donde están los nodos
    margen: float = 0.9
    figura.update_layout(
        showlegend=False,
        height=560,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor=NEGRO,
        plot_bgcolor=NEGRO,
        xaxis={
            "visible": False,
            "fixedrange": True,
            "range": [min(xs) - margen, max(xs) + margen],
        },
        yaxis={
            "visible": False,
            "fixedrange": True,
            "scaleanchor": "x",
            "range": [min(ys) - margen, max(ys) + margen],
        },
        hoverlabel={
            "bgcolor": NEGRO,
            "bordercolor": NARANJA,
            "font": {"color": CREMA},
        },
    )
    return figura


def armar_chips(ruta: List[str]) -> str:
    # Una caja por nodo; el retraso las muestra una tras otra
    piezas: List[str] = []

    for posicion, nombre in enumerate(ruta):
        retraso: float = posicion * 0.1
        piezas.append(
            f'<span class="nodo-ruta" style="animation-delay: {retraso:.1f}s">'
            f"{html.escape(nombre)}</span>"
        )

    return '<span class="flecha-ruta">→</span>'.join(piezas)


def mostrar_registro(grafo: Grafo) -> None:
    with st.sidebar:
        st.header("Agregar conexión")
        st.caption("Se muestra en el mapa en cuanto la guardas.")

        with st.form("form_conexion", clear_on_submit=True):
            origen: str = st.text_input("Origen")
            destino: str = st.text_input("Destino")
            peso: str = st.text_input("Distancia o costo")
            enviado: bool = st.form_submit_button("Guardar conexión")

        if not enviado:
            return

        try:
            origen, destino, peso_numero = io_handler.validar_conexion(
                origen, destino, peso
            )
            io_handler.guardar_conexion((origen, destino, peso_numero))
        except ValueError as error:
            st.error(f"Revisa los datos: {error}")
        except PermissionError:
            st.error("No hay permiso para escribir en nodos.csv.")
        except OSError:
            st.error("No se pudo guardar en nodos.csv.")
        else:
            # Solo si se guardó en disco se actualiza el grafo en memoria
            for nombre in (origen, destino):
                if nombre not in grafo.nodos:
                    grafo.agregar_nodo(nombre)
            grafo.agregar_conexion(origen, destino, peso_numero)
            st.session_state["nueva_arista"] = (origen, destino)
            st.success(f"Conexión {origen} - {destino} guardada.")
            st.toast("Conexión agregada al mapa")


def mostrar_panel(
    grafo: Grafo, origen: str, destino: str, costo: float, ruta: List[str]
) -> None:
    st.subheader("Tu ruta")
    st.text_input("Origen", key="origen_calc", placeholder="Ej. A")
    st.text_input("Destino", key="destino_calc", placeholder="Ej. E")
    st.button("Limpiar selección", on_click=limpiar_seleccion)

    if origen == "" and destino == "":
        st.info("Elige dos nodos en el mapa, o escríbelos aquí.")
    elif origen == "" or destino == "":
        st.info("Falta elegir el otro nodo.")
    elif origen not in grafo.nodos or destino not in grafo.nodos:
        st.error("Ese nodo no existe en el mapa, revisa cómo lo escribiste.")
    elif origen == destino:
        st.info("El origen y el destino son el mismo nodo.")
    elif len(ruta) == 0:
        st.warning(f"No hay un camino entre {origen} y {destino}.")
    else:
        st.metric("Costo total", f"{costo:g}")
        st.markdown(armar_chips(ruta), unsafe_allow_html=True)


def mostrar_tabla(grafo: Grafo) -> None:
    # Filas de la tabla, una por conexión
    filas = [
        {"Origen": a, "Destino": b, "Distancia": f"{peso:g}"}
        for a, b, peso in lista_aristas(grafo)
    ]

    if len(filas) == 0:
        st.info("Todavía no hay conexiones.")
        return

    tabla = pd.DataFrame(filas)
    tabla.index = range(1, len(tabla) + 1)
    st.table(tabla)


def main() -> None:
    st.set_page_config(page_title="Calculadora de nodos", layout="wide")
    st.markdown(ESTILOS, unsafe_allow_html=True)
    st.title("Calculadora de nodos")
    st.caption(
        "Toca dos nodos del mapa para ver la ruta más corta. También puedes "
        "tocar el rombo de una conexión para elegirla."
    )

    cargar_grafo_una_vez()
    iniciar_estado()

    # Grafo guardado en memoria durante toda la sesión
    grafo: Grafo = st.session_state["grafo"]

    # El formulario va antes del mapa para que la conexión nueva se dibuje ya
    mostrar_registro(grafo)
    acomodar_nodos(grafo, st.session_state["posiciones"])

    # Nodos elegidos (por toque o escritos) y su ruta más corta
    origen: str = st.session_state["origen_calc"].strip().upper()
    destino: str = st.session_state["destino_calc"].strip().upper()
    costo, ruta = buscar_recorrido(grafo, origen, destino)

    col_mapa, col_panel = st.columns([3, 2])

    with col_mapa:
        if len(grafo.nodos) == 0:
            st.info("Aún no hay conexiones. Agrega la primera en la barra.")
        else:
            st.plotly_chart(
                construir_figura(
                    grafo, st.session_state["posiciones"],
                    origen, destino, ruta,
                ),
                key=f"mapa_{st.session_state['version_mapa']}",
                on_select=al_tocar_mapa,
                selection_mode="points",
                config={"displayModeBar": False},
            )

    with col_panel:
        mostrar_panel(grafo, origen, destino, costo, ruta)

    with st.expander("Ver todas las conexiones"):
        mostrar_tabla(grafo)


main()