from typing import Dict, List, Optional, Set, Tuple


class Nodo:
    def __init__(self, nombre: str) -> None:
        # Nombre del nodo, sirve para identificarlo en el grafo
        self.nombre: str = nombre

        # Vecinos {nombre: peso}, sirve para saber con quién se conecta
        self.vecinos: Dict[str, float] = {}


class Grafo:
    def __init__(self) -> None:
        # Todos los nodos {nombre: Nodo}, sirve para buscarlos rápido
        self.nodos: Dict[str, Nodo] = {}

    def agregar_nodo(self, nombre: str) -> None:
        self.nodos[nombre] = Nodo(nombre)

    def agregar_conexion(self, origen: str, destino: str, peso: float) -> None:
        self.nodos[origen].vecinos[destino] = peso
        self.nodos[destino].vecinos[origen] = peso

    def dijkstra(self, inicio: str, destino: str) -> Tuple[float, List[str]]:
        # Menor costo conocido hasta cada nodo
        distancias: Dict[str, float] = {}

        # Nodo previo de cada nodo, sirve para armar la ruta al final
        anteriores: Dict[str, Optional[str]] = {}

        # Nodos con costo ya confirmado
        visitados: Set[str] = set()

        for nombre in self.nodos:
            distancias[nombre] = float("inf")
            anteriores[nombre] = None

        distancias[inicio] = 0

        while len(visitados) < len(self.nodos):
            # Nodo no visitado más cercano en esta vuelta
            nodo_actual: Optional[str] = None

            # Menor distancia encontrada en esta vuelta
            menor_distancia: float = float("inf")

            for nombre in self.nodos:
                if nombre not in visitados:
                    if distancias[nombre] < menor_distancia:
                        menor_distancia = distancias[nombre]
                        nodo_actual = nombre

            if nodo_actual is None or nodo_actual == destino:
                break

            visitados.add(nodo_actual)

            # Se revisan los vecinos del nodo actual
            for vecino, peso in self.nodos[nodo_actual].vecinos.items():
                # Costo de llegar al vecino pasando por el nodo actual
                nueva_distancia: float = distancias[nodo_actual] + peso

                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    anteriores[vecino] = nodo_actual

        # Si el destino sigue en infinito, no hay camino
        if distancias[destino] == float("inf"):
            return float("inf"), []

        # Ruta armada desde el destino hacia atrás
        ruta: List[str] = []
        actual: Optional[str] = destino

        while actual is not None:
            ruta.append(actual)
            actual = anteriores[actual]

        ruta.reverse()
        return distancias[destino], ruta
