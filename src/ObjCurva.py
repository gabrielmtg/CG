import math
import tkinter as tk
from typing import List, Tuple

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic
from src.Transform import Transform

Ponto = Tuple[float, float]


class ObjCurva(ObjGrafic):
    MATRIZ_BEZIER = [[-1.0,  3.0, -3.0, 1.0],
                     [3.0, -6.0,  3.0, 0.0],
                     [-3.0,  3.0,  0.0, 0.0],
                     [1.0,  0.0,  0.0, 0.0]]
    PASSOS_MIN = 10
    PASSOS_MAX = 300

    def __init__(self, canvas: tk.Canvas, name: str, color: str, points: List[Ponto]):
        super().__init__(canvas, name, color, "curva", points)

    @staticmethod
    def quantidade_valida(n: int) -> bool:
        return n >= 4 and (n - 1) % 3 == 0

    def move_point(self, index: int, dx: float, dy: float):
        if index < 0 or index >= len(self.points):
            return
        self.points[index][0] += dx
        self.points[index][1] += dy

    @staticmethod
    def segmentos(controle: List[Ponto]) -> List[List[Ponto]]:
        return [controle[i:i + 4] for i in range(0, len(controle) - 3, 3)]

    @staticmethod
    def blending(t: float) -> List[float]:
        return Transform.mult_matrix([[t ** 3, t ** 2, t, 1.0]], ObjCurva.MATRIZ_BEZIER)[0]

    @staticmethod
    def ponto_bezier(t: float, geometria: List[Ponto]) -> Ponto:
        b = ObjCurva.blending(t)
        x = sum(b[j] * geometria[j][0] for j in range(4))
        y = sum(b[j] * geometria[j][1] for j in range(4))
        return x, y

    @staticmethod
    def passos(geometria: List[Ponto]) -> int:
        comprimento = sum(math.dist(geometria[i], geometria[i + 1]) for i in range(3))
        return max(ObjCurva.PASSOS_MIN, min(ObjCurva.PASSOS_MAX, int(comprimento * 100)))

    def gerar_pontos(self, controle: List[Ponto]) -> List[Ponto]:
        curva: List[Ponto] = []
        for geometria in self.segmentos(controle):
            n = self.passos(geometria)
            inicio = 1 if curva else 0
            for i in range(inicio, n + 1):
                curva.append(self.ponto_bezier(i / n, geometria))
        return curva

    def draw(self, clipping: Clipping, transform):
        self.erase()
        pontos = self.gerar_pontos(self.scn_points)
        if len(pontos) < 2:
            return
        anterior = pontos[0]
        anterior_dentro = clipping.ponto(anterior) is not None
        for atual in pontos[1:]:
            atual_dentro = clipping.ponto(atual) is not None
            if anterior_dentro and atual_dentro:
                segmento = (anterior, atual)
            else:
                segmento = clipping.reta(anterior, atual)
            if segmento is not None:
                (x0, y0), (x1, y1) = segmento
                sx0, sy0 = transform(x0, y0)
                sx1, sy1 = transform(x1, y1)
                self.ids_obj.append(self.canvas.create_line(
                    sx0, sy0, sx1, sy1, fill=self.color, width=3, tags=self.name
                ))
            anterior, anterior_dentro = atual, atual_dentro
