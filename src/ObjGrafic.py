from abc import ABC, abstractmethod
import tkinter as tk
from typing import List, Tuple

from src.Transform import Transform, Matriz


class ObjGrafic(ABC):

    def __init__(self, canvas: tk.Canvas, name: str, color: str, tipo: str, points: List[Tuple[float, float]]):
        self.canvas = canvas
        self.name = name
        self.color = color
        self.tipo = tipo
        self.points = [list(p) for p in points]
        self.ids_obj = []

    @abstractmethod
    def draw(self, transform):
        pass

    def erase(self):
        for id_obj in self.ids_obj:
            self.canvas.delete(id_obj)
        self.ids_obj = []

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
