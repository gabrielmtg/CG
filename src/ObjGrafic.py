from abc import ABC, abstractmethod
import tkinter as tk
from typing import Callable, List, Optional, Sequence, Tuple

from src.Clipping import Clipping
from src.Ponto3D import Ponto3D
from src.Transform import Transform, Matriz


class ObjGrafic(ABC):

    def __init__(self, canvas: tk.Canvas, name: str, color: str, tipo: str,
                 points: Sequence[Sequence[float]]):
        self.canvas = canvas
        self.name = name
        self.color = color
        self.tipo = tipo
        self.points: List[Ponto3D] = [Ponto3D(*Transform.como_3d(p)) for p in points]
        self.scn_points: List[Optional[Tuple[float, float]]] = []
        self.ids_obj = []

    @abstractmethod
    def draw(self, clipping: Clipping, transform):
        pass

    def erase(self):
        for id_obj in self.ids_obj:
            self.canvas.delete(id_obj)
        self.ids_obj = []

    def update_scn(self, projetar: Callable[[Sequence[float]], Optional[Tuple[float, float]]]):
        self.scn_points = [projetar(p.coords()) for p in self.points]

    def apply_transform(self, matriz: Matriz):
        Transform.aplicar(matriz, self)

    def move(self, dx: float, dy: float, dz: float = 0.0):
        self.apply_transform(Transform.matriz_translacao(dx, dy, dz))

    def escalonar(self, sx: float, sy: float, sz: float = 1.0):
        self.apply_transform(Transform.matriz_escala_natural(sx, sy, sz, self.get_center()))

    def rotacionar(self, graus: float, ponto: Sequence[float], direcao: Sequence[float]):
        self.apply_transform(Transform.matriz_rotacao_eixo(graus, ponto, direcao))

    def move_point(self, index: int, dx: float, dy: float, dz: float = 0.0):
        if 0 <= index < len(self.points):
            self.points[index].transladar(dx, dy, dz)

    def get_name(self) -> str:
        return self.name

    def get_color(self) -> str:
        return self.color

    def get_type(self) -> str:
        return self.tipo

    def get_points(self) -> List[Tuple[float, float, float]]:
        return [p.coords() for p in self.points]

    def set_points(self, points: Sequence[Sequence[float]]):
        if len(points) == len(self.points):
            for p, novo in zip(self.points, points):
                p.set(*Transform.como_3d(novo))
        else:
            self.points = [Ponto3D(*Transform.como_3d(p)) for p in points]

    def get_center(self) -> Tuple[float, float, float]:
        return Transform.centro_geometrico(self.get_points())

    def desenhar_curva_recortada(self, pontos: List[Tuple[float, float]], clipping: Clipping, transform):
        if len(pontos) < 2:
            return
        anterior = pontos[0]
        anterior_dentro = anterior is not None and clipping.ponto(anterior) is not None
        for atual in pontos[1:]:
            atual_dentro = atual is not None and clipping.ponto(atual) is not None
            if anterior_dentro and atual_dentro:
                self.desenhar_segmento((anterior, atual), transform)
            else:
                self.desenhar_segmento_recortado(anterior, atual, clipping, transform)
            anterior, anterior_dentro = atual, atual_dentro

    def desenhar_segmento_recortado(self, a, b, clipping: Clipping, transform):
        if a is None or b is None:
            return
        segmento = clipping.reta(a, b)
        if segmento is not None:
            self.desenhar_segmento(segmento, transform)

    def desenhar_polilinha_recortada(self, pontos, clipping: Clipping, transform, largura: int = 3):
        trecho = []

        def fechar_trecho():
            if len(trecho) >= 2:
                coords = [c for x, y in trecho for c in transform(x, y)]
                self.ids_obj.append(self.canvas.create_line(
                    *coords, fill=self.color, width=largura, tags=self.name
                ))
            trecho.clear()

        for anterior, atual in zip(pontos, pontos[1:]):
            if anterior is None or atual is None:
                fechar_trecho()
                continue
            anterior_dentro = clipping.ponto(anterior) is not None
            atual_dentro = clipping.ponto(atual) is not None
            if anterior_dentro and atual_dentro:
                if not trecho:
                    trecho.append(anterior)
                trecho.append(atual)
                continue
            segmento = clipping.reta(anterior, atual)
            if segmento is None:
                fechar_trecho()
            elif anterior_dentro:
                if not trecho:
                    trecho.append(anterior)
                trecho.append(segmento[1])
                fechar_trecho()
            else:
                fechar_trecho()
                trecho.extend(segmento)
                if not atual_dentro:
                    fechar_trecho()
        fechar_trecho()

    def desenhar_segmento(self, segmento, transform):
        (x0, y0), (x1, y1) = segmento
        sx0, sy0 = transform(x0, y0)
        sx1, sy1 = transform(x1, y1)
        self.ids_obj.append(self.canvas.create_line(
            sx0, sy0, sx1, sy1, fill=self.color, width=3, tags=self.name
        ))
