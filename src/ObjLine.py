import tkinter as tk
from typing import Sequence

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic


class ObjLine(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 p0: Sequence[float], p1: Sequence[float]):
        super().__init__(canvas, name, color, "reta", [p0, p1])

    def draw(self, clipping: Clipping, transform):
        self.erase()
        self.desenhar_segmento_recortado(*self.scn_points, clipping, transform)
