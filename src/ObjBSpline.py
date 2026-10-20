import math
import tkinter as tk
from typing import List, Tuple

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic
from src.Transform import Transform

Ponto = Tuple[float, float]


class ObjBSpline(ObjGrafic):
    MATRIZ_BSPLINE = [[-1 / 6,  3 / 6, -3 / 6, 1 / 6],
                      [3 / 6, -6 / 6,  3 / 6, 0.0],
                      [-3 / 6,  0.0,    3 / 6, 0.0],
                      [1 / 6,  4 / 6,  1 / 6, 0.0]]
    MINIMO_PONTOS = 4
    PASSOS_MIN = 10
    PASSOS_MAX = 300

    def __init__(self, canvas: tk.Canvas, name: str, color: str, points: List[Ponto]):
        super().__init__(canvas, name, color, "bspline", points)

    @staticmethod
    def quantidade_valida(n: int) -> bool:
        return n >= ObjBSpline.MINIMO_PONTOS

    def move_point(self, index: int, dx: float, dy: float):
        if index < 0 or index >= len(self.points):
            return
        self.points[index][0] += dx
        self.points[index][1] += dy

    @staticmethod
    def geometrias(controle: List[Ponto]) -> List[List[Ponto]]:
        return [controle[i - 3:i + 1] for i in range(3, len(controle))]

    @staticmethod
    def coeficientes(geometria: List[Ponto]) -> List[List[float]]:
        return Transform.mult_matrix(ObjBSpline.MATRIZ_BSPLINE, [[x, y] for x, y in geometria])

    @staticmethod
    def matriz_diferencas(delta: float) -> List[List[float]]:
        d1, d2, d3 = delta, delta ** 2, delta ** 3
        return [[0.0,     0.0,     0.0, 1.0],
                [d3,      d2,      d1,  0.0],
                [6 * d3,  2 * d2,  0.0, 0.0],
                [6 * d3,  0.0,     0.0, 0.0]]

    @staticmethod
    def diferencas_iniciais(geometria: List[Ponto], passos: int) -> List[List[float]]:
        return Transform.mult_matrix(ObjBSpline.matriz_diferencas(1.0 / passos),
                                     ObjBSpline.coeficientes(geometria))

    @staticmethod
    def forward_differences(diferencas: List[List[float]], passos: int) -> List[Ponto]:
        (x, y), (dx, dy), (d2x, d2y), (d3x, d3y) = diferencas
        pontos = [(x, y)]
        for _ in range(passos):
            x, dx, d2x = x + dx, dx + d2x, d2x + d3x
            y, dy, d2y = y + dy, dy + d2y, d2y + d3y
            pontos.append((x, y))
        return pontos

    @staticmethod
    def passos(geometria: List[Ponto]) -> int:
        comprimento = sum(math.dist(geometria[i], geometria[i + 1]) for i in range(3))
        return max(ObjBSpline.PASSOS_MIN, min(ObjBSpline.PASSOS_MAX, int(comprimento * 100)))

    def gerar_pontos(self, controle: List[Ponto]) -> List[Ponto]:
        curva: List[Ponto] = []
        for geometria in self.geometrias(controle):
            n = self.passos(geometria)
            pontos = self.forward_differences(self.diferencas_iniciais(geometria, n), n)
            curva.extend(pontos[1:] if curva else pontos)
        return curva

    def draw(self, clipping: Clipping, transform):
        self.erase()
        self.desenhar_curva_recortada(self.gerar_pontos(self.scn_points), clipping, transform)
