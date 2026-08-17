import tkinter as tk
from src.ObjGrafic import ObjGrafic


class ObjLine(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str, x0: float, y0: float, x1: float, y1: float):
        super().__init__(canvas, name, color, "reta", [(x0, y0), (x1, y1)])

    def move_point(self, index: int, dx: float, dy: float):
        if index not in (0, 1):
            return
        self.points[index][0] += dx
        self.points[index][1] += dy

    def draw(self, transform):
        self.erase()
        (x0, y0), (x1, y1) = self.points
        sx0, sy0 = transform(x0, y0)
        sx1, sy1 = transform(x1, y1)
        self.ids_obj.append(self.canvas.create_line(
            sx0, sy0, sx1, sy1, fill=self.color, width=3, tags=self.name
        ))
