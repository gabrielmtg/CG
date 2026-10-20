import tkinter as tk
from typing import List, Sequence, Tuple

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic
from src.Ponto3D import Ponto3D


class Objeto3D(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 vertices: Sequence[Sequence[float]], arestas: Sequence[Tuple[int, int]]):
        super().__init__(canvas, name, color, "objeto3d", vertices)
        for i, j in arestas:
            if not (0 <= i < len(self.points) and 0 <= j < len(self.points)):
                raise ValueError(f"Aresta ({i + 1}, {j + 1}) usa um vértice inexistente.")
        self.segmentos: List[Tuple[Ponto3D, Ponto3D]] = [(self.points[i], self.points[j]) for i, j in arestas]

    def get_arestas(self) -> List[Tuple[int, int]]:
        indice = {id(p): i for i, p in enumerate(self.points)}
        return [(indice[id(a)], indice[id(b)]) for a, b in self.segmentos]

    def draw(self, clipping: Clipping, transform):
        self.erase()
        for i, j in self.get_arestas():
            segmento = clipping.reta(self.scn_points[i], self.scn_points[j])
            if segmento is not None:
                self.desenhar_segmento(segmento, transform)
