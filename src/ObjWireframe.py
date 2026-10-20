import tkinter as tk
from typing import List, Tuple

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic


class ObjWireframe(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 points: List[Tuple[float, float]], closed: bool = True, filled: bool = False):
        super().__init__(canvas, name, color, "wireframe", points)
        self.closed = closed or filled
        self.filled = filled

    def draw(self, clipping: Clipping, transform):
        self.erase()
        if self.filled:
            self._draw_filled(clipping, transform)
        else:
            self._draw_edges(clipping, transform)

    def _draw_filled(self, clipping: Clipping, transform):
        poligono = clipping.poligono(self.scn_points)
        if len(poligono) < 3:
            return
        coords = [c for x, y in poligono for c in transform(x, y)]
        self.ids_obj.append(self.canvas.create_polygon(
            coords, fill=self.color, outline=self.color, width=1, tags=self.name
        ))

    def _draw_edges(self, clipping: Clipping, transform):
        n = len(self.scn_points)
        last_segment = n if self.closed else n - 1
        for i in range(last_segment):
            segmento = clipping.reta(self.scn_points[i], self.scn_points[(i + 1) % n])
            if segmento is not None:
                self.desenhar_segmento(segmento, transform)
