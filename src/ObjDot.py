import tkinter as tk

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic


class ObjDot(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str, pos_x: float, pos_y: float):
        super().__init__(canvas, name, color, "ponto", [(pos_x, pos_y)])

    def get_position_x(self) -> float:
        return self.points[0][0]

    def get_position_y(self) -> float:
        return self.points[0][1]

    def draw(self, clipping: Clipping, transform, radius: float = 3):
        self.erase()
        ponto = clipping.ponto(self.scn_points[0])
        if ponto is None:
            return
        sx, sy = transform(*ponto)
        self.ids_obj.append(self.canvas.create_oval(
            sx - radius, sy - radius, sx + radius, sy + radius,
            fill=self.color, outline=self.color, tags=self.name
        ))
