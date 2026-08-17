import tkinter as tk
from typing import List, Tuple
from src.ObjGrafic import ObjGrafic


class ObjWireframe(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 points: List[Tuple[float, float]], closed: bool = True):
        super().__init__(canvas, name, color, "wireframe", points)
        self.closed = closed

    def move_point(self, index: int, dx: float, dy: float):
        if index < 0 or index >= len(self.points):
            return
        self.points[index][0] += dx
        self.points[index][1] += dy

    def draw(self, transform):
        self.erase()
        screen_points = [transform(x, y) for x, y in self.points]
        n = len(screen_points)
        last_segment = n if self.closed else n - 1
        for i in range(last_segment):
            x0, y0 = screen_points[i]
            x1, y1 = screen_points[(i + 1) % n]
            self.ids_obj.append(self.canvas.create_line(
                x0, y0, x1, y1, fill=self.color, width=3, tags=self.name
            ))
