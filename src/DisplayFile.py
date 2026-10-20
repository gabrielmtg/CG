import tkinter as tk
from typing import Dict, Iterable

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic
from src.Transform import Matriz
from src.Viewport import Viewport
from src.Window import Window


class DisplayFile:

    def __init__(self, canvas: tk.Canvas, window: Window, viewport: Viewport, clipping: Clipping = None):
        self.canvas = canvas
        self.window = window
        self.viewport = viewport
        self.clipping = clipping if clipping is not None else Clipping()
        self.objects: Dict[str, ObjGrafic] = {}
        self.observadores_window = []

    def gerar_descricao_scn(self):
        matriz_scn = self.window.matriz_scn()
        for obj in self.objects.values():
            obj.update_scn(matriz_scn)

    def _desenhar(self, obj: ObjGrafic):
        obj.update_scn(self.window.matriz_scn())
        obj.draw(self.clipping, self.viewport.transform)

    def redraw_all(self):
        self.gerar_descricao_scn()
        for obj in self.objects.values():
            obj.draw(self.clipping, self.viewport.transform)

    def set_algoritmo_reta(self, algoritmo: str):
        self.clipping.algoritmo_reta = algoritmo
        self.redraw_all()

    def add(self, obj: ObjGrafic):
        self.objects[obj.get_name()] = obj
        self._desenhar(obj)

    def add_all(self, objetos: Iterable[ObjGrafic]):
        for obj in objetos:
            self.add(obj)

    def remove(self, name: str):
        obj = self.objects.pop(name, None)
        if obj is not None:
            obj.erase()

    def clear(self):
        for obj in self.objects.values():
            obj.erase()
        self.objects.clear()

    def move_object(self, name: str, dx: float, dy: float, dz: float = 0.0):
        obj = self.objects.get(name)
        if obj is not None:
            obj.move(*self.window.to_world_vector(dx, dy, dz))
            self._desenhar(obj)

    def transform_object(self, name: str, matriz: Matriz):
        obj = self.objects.get(name)
        if obj is not None:
            obj.apply_transform(matriz)
            self._desenhar(obj)

    def move_point(self, name: str, index: int, dx: float, dy: float, dz: float = 0.0):
        obj = self.objects.get(name)
        if obj is not None:
            obj.move_point(index, *self.window.to_world_vector(dx, dy, dz))
            self._desenhar(obj)

    def find_object_at(self, sx: float, sy: float, halo: int = 5):
        ids = set(self.canvas.find_overlapping(sx - halo, sy - halo, sx + halo, sy + halo))
        for obj in self.objects.values():
            if ids.intersection(obj.ids_obj):
                return obj.get_name()
        return None

    def _window_mudou(self):
        self.redraw_all()
        for observador in self.observadores_window:
            observador()

    def pan(self, dx: float, dy: float, dz: float = 0.0):
        self.window.pan(dx, dy, dz)
        self._window_mudou()

    def zoom(self, factor: float):
        self.window.zoom(factor)
        self._window_mudou()

    def rotate_window(self, graus: float):
        self.window.rotate(graus)
        self._window_mudou()

    def rotate_window_x(self, graus: float):
        self.window.rotate_x(graus)
        self._window_mudou()

    def rotate_window_y(self, graus: float):
        self.window.rotate_y(graus)
        self._window_mudou()

    def orbitar_window(self, graus_x: float, graus_y: float):
        self.window.rotate_x(graus_x)
        self.window.rotate_y(graus_y)
        self._window_mudou()

    def resetar_window(self):
        self.window.resetar()
        self._window_mudou()
