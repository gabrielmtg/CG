import tkinter as tk
from src.ObjGrafic import ObjGrafic


class ObjDot(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str, pos_x: float, pos_y: float):
        super().__init__(canvas, name, color, "ponto", [(pos_x, pos_y)])

    def get_position_x(self) -> float:
        return self.points[0][0]

    def get_position_y(self) -> float:
        return self.points[0][1]

    def draw(self, transform, radius: float = 3):
        self.erase()
        x, y = self.points[0]
        sx, sy = transform(x, y)
        self.ids_obj.append(self.canvas.create_oval(
            sx - radius, sy - radius, sx + radius, sy + radius,
            fill=self.color, outline=self.color, tags=self.name
        ))
