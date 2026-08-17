import tkinter as tk
from typing import Dict

from src.ObjGrafic import ObjGrafic
from src.Viewport import Viewport


class DisplayFile:

    def __init__(self, canvas: tk.Canvas, viewport: Viewport):
        self.canvas = canvas
        self.viewport = viewport
        self.objects: Dict[str, ObjGrafic] = {}

    def add(self, obj: ObjGrafic):
        self.objects[obj.get_name()] = obj
        obj.draw(self.viewport.transform)

    def remove(self, name: str):
        obj = self.objects.pop(name, None)
        if obj is not None:
            obj.erase()

    def redraw_all(self):
        for obj in self.objects.values():
            obj.draw(self.viewport.transform)

    def move_object(self, name: str, dx: float, dy: float):
        obj = self.objects.get(name)
        if obj is not None:
            obj.move(dx, dy)
            obj.draw(self.viewport.transform)

    def move_point(self, name: str, index: int, dx: float, dy: float):
        obj = self.objects.get(name)
        if obj is not None and hasattr(obj, "move_point"):
            obj.move_point(index, dx, dy)
            obj.draw(self.viewport.transform)

    def pan(self, dx: float, dy: float):
        self.viewport.pan(dx, dy)
        self.redraw_all()

    def zoom(self, factor: float):
        self.viewport.zoom(factor)
        self.redraw_all()
