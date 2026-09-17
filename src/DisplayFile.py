import tkinter as tk
from typing import Dict, Iterable

from src.ObjGrafic import ObjGrafic
from src.Transform import Matriz
from src.Viewport import Viewport
from src.Window import Window


class DisplayFile:

    def __init__(self, canvas: tk.Canvas, window: Window, viewport: Viewport):
        self.canvas = canvas
        self.window = window
        self.viewport = viewport
        self.objects: Dict[str, ObjGrafic] = {}

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def gerar_descricao_scn(self):
        """Recalcula a cache em SCN de todos os objetos a partir da window atual."""
        matriz_scn = self.window.matriz_scn()
        for obj in self.objects.values():
            obj.update_scn(matriz_scn)

    def _desenhar(self, obj: ObjGrafic):
        obj.update_scn(self.window.matriz_scn())
        obj.draw(self.viewport.transform)

    def redraw_all(self):
        self.gerar_descricao_scn()
        for obj in self.objects.values():
            obj.draw(self.viewport.transform)

    # ------------------------------------------------------------------
    # Objetos
    # ------------------------------------------------------------------
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

    def move_object(self, name: str, dx: float, dy: float):
        """Translada o objeto; (dx, dy) é dado no referencial do usuário
        (o "para cima" é o cima da tela, mesmo com a window rotacionada)."""
        obj = self.objects.get(name)
        if obj is not None:
            obj.move(*self.window.to_world_vector(dx, dy))
            self._desenhar(obj)

    def transform_object(self, name: str, matriz: Matriz):
        obj = self.objects.get(name)
        if obj is not None:
            obj.apply_transform(matriz)
            self._desenhar(obj)

    def move_point(self, name: str, index: int, dx: float, dy: float):
        obj = self.objects.get(name)
        if obj is not None and hasattr(obj, "move_point"):
            obj.move_point(index, *self.window.to_world_vector(dx, dy))
            self._desenhar(obj)

    def find_object_at(self, sx: float, sy: float, halo: int = 5):
        ids = set(self.canvas.find_overlapping(sx - halo, sy - halo, sx + halo, sy + halo))
        for obj in self.objects.values():
            if ids.intersection(obj.ids_obj):
                return obj.get_name()
        return None

    # ------------------------------------------------------------------
    # Navegação da window
    # ------------------------------------------------------------------
    def pan(self, dx: float, dy: float):
        self.window.pan(dx, dy)
        self.redraw_all()

    def zoom(self, factor: float):
        self.window.zoom(factor)
        self.redraw_all()

    def rotate_window(self, graus: float):
        self.window.rotate(graus)
        self.redraw_all()
