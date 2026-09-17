from abc import ABC, abstractmethod
import tkinter as tk
from typing import List, Tuple

from src.Transform import Transform, Matriz


class ObjGrafic(ABC):
    """Objeto gráfico do mundo.

    `points` guarda as coordenadas do mundo (WC) e nunca é alterado pela
    navegação da window. `scn_points` é a cache da descrição do objeto no
    Sistema de Coordenadas Normalizado (SCN), recalculada pelo display file
    sempre que a window ou o objeto mudam; é ela que vai para a viewport.
    """

    def __init__(self, canvas: tk.Canvas, name: str, color: str, tipo: str, points: List[Tuple[float, float]]):
        self.canvas = canvas
        self.name = name
        self.color = color
        self.tipo = tipo
        self.points = [list(p) for p in points]
        self.scn_points: List[Tuple[float, float]] = []
        self.ids_obj = []

    @abstractmethod
    def draw(self, transform):
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
