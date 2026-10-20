from abc import ABC, abstractmethod
import tkinter as tk
from typing import List, Tuple

from src.Clipping import Clipping
from src.Transform import Transform, Matriz


class ObjGrafic(ABC):

    def __init__(self, canvas: tk.Canvas, name: str, color: str, tipo: str, points: List[Tuple[float, float]]):
        self.canvas = canvas
        self.name = name
        self.color = color
        self.tipo = tipo
        self.points = [list(p) for p in points]
        self.scn_points: List[Tuple[float, float]] = []
        self.ids_obj = []

    @abstractmethod
    def draw(self, clipping: Clipping, transform):
        pass

    def erase(self):
        for id_obj in self.ids_obj:
            self.canvas.delete(id_obj)
        self.ids_obj = []

    def update_scn(self, matriz_scn: Matriz):
        self.scn_points = Transform.aplicar_pontos(matriz_scn, self.get_points())

    def apply_transform(self, matriz: Matriz):
        Transform.aplicar(matriz, self)

    def move(self, dx: float, dy: float):
        self.apply_transform(Transform.matriz_translacao(dx, dy))

    def get_name(self) -> str:
        return self.name

    def get_color(self) -> str:
        return self.color

    def get_type(self) -> str:
        return self.tipo

    def get_points(self) -> List[Tuple[float, float]]:
        return [tuple(p) for p in self.points]

    def set_points(self, points: List[Tuple[float, float]]):
        self.points = [list(p) for p in points]

    def get_center(self) -> Tuple[float, float]:
        return Transform.centro_geometrico(self.points)

    def desenhar_curva_recortada(self, pontos: List[Tuple[float, float]], clipping: Clipping, transform):
        if len(pontos) < 2:
            return
        anterior = pontos[0]
        anterior_dentro = clipping.ponto(anterior) is not None
        for atual in pontos[1:]:
            atual_dentro = clipping.ponto(atual) is not None
            if anterior_dentro and atual_dentro:
                segmento = (anterior, atual)
            else:
                segmento = clipping.reta(anterior, atual)
            if segmento is not None:
                (x0, y0), (x1, y1) = segmento
                sx0, sy0 = transform(x0, y0)
                sx1, sy1 = transform(x1, y1)
                self.ids_obj.append(self.canvas.create_line(
                    sx0, sy0, sx1, sy1, fill=self.color, width=3, tags=self.name
                ))
            anterior, anterior_dentro = atual, atual_dentro
