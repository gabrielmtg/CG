import tkinter as tk

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic


class ObjDot(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 pos_x: float, pos_y: float, pos_z: float = 0.0):
        super().__init__(canvas, name, color, "ponto", [(pos_x, pos_y, pos_z)])

    def get_position_x(self) -> float:
        return self.points[0].x

    def get_position_y(self) -> float:
        return self.points[0].y

    def get_position_z(self) -> float:
        return self.points[0].z

    def draw(self, clipping: Clipping, transform, radius: float = 3):
        self.erase()
        ponto = self.scn_points[0]
        if ponto is None or clipping.ponto(ponto) is None:
            return
        sx, sy = transform(*ponto)
        self.ids_obj.append(self.canvas.create_oval(
            sx - radius, sy - radius, sx + radius, sy + radius,
            fill=self.color, outline=self.color, tags=self.name
        ))
