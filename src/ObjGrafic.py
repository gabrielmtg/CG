from abc import ABC, abstractmethod
import tkinter as tk
from typing import List, Tuple


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

    def move(self, dx: float, dy: float):
        for p in self.points:
            p[0] += dx
            p[1] += dy

    def get_name(self) -> str:
        return self.name

    def get_color(self) -> str:
        return self.color

    def get_type(self) -> str:
        return self.tipo

    def get_points(self) -> List[Tuple[float, float]]:
        return [tuple(p) for p in self.points]
