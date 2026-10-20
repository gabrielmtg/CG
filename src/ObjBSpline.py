import tkinter as tk
from typing import List, Optional, Sequence, Tuple

from src.ObjCurvaParametrica import ObjCurvaParametrica
from src.Transform import Transform

Ponto = Tuple[float, float, float]


class ObjBSpline(ObjCurvaParametrica):
    MATRIZ_BSPLINE = [[-1 / 6,  3 / 6, -3 / 6, 1 / 6],
                      [3 / 6, -6 / 6,  3 / 6, 0.0],
                      [-3 / 6,  0.0,    3 / 6, 0.0],
                      [1 / 6,  4 / 6,  1 / 6, 0.0]]
    MINIMO_PONTOS = 4

    def __init__(self, canvas: tk.Canvas, name: str, color: str, points: Sequence[Sequence[float]]):
        super().__init__(canvas, name, color, "bspline", points)

    @staticmethod
    def quantidade_valida(n: int) -> bool:
        return n >= ObjBSpline.MINIMO_PONTOS

    @staticmethod
    def geometrias(controle: Sequence) -> List[list]:
        return [list(controle[i - 3:i + 1]) for i in range(3, len(controle))]

    @staticmethod
    def coeficientes(geometria: Sequence[Sequence[float]]) -> List[List[float]]:
        return Transform.mult_matrix(ObjBSpline.MATRIZ_BSPLINE, [list(Transform.como_3d(p)) for p in geometria])

    @staticmethod
    def matriz_diferencas(delta: float) -> List[List[float]]:
        d1, d2, d3 = delta, delta ** 2, delta ** 3
        return [[0.0,     0.0,     0.0, 1.0],
                [d3,      d2,      d1,  0.0],
                [6 * d3,  2 * d2,  0.0, 0.0],
                [6 * d3,  0.0,     0.0, 0.0]]

    @staticmethod
    def diferencas_iniciais(geometria: Sequence[Sequence[float]], passos: int) -> List[List[float]]:
        return Transform.mult_matrix(ObjBSpline.matriz_diferencas(1.0 / passos),
                                     ObjBSpline.coeficientes(geometria))

    @staticmethod
    def forward_differences(diferencas: List[List[float]], passos: int) -> List[Ponto]:
        (x, y, z), (dx, dy, dz), (d2x, d2y, d2z), (d3x, d3y, d3z) = diferencas
        pontos = [(x, y, z)]
        for _ in range(passos):
            x, dx, d2x = x + dx, dx + d2x, d2x + d3x
            y, dy, d2y = y + dy, dy + d2y, d2y + d3y
            z, dz, d2z = z + dz, dz + d2z, d2z + d3z
            pontos.append((x, y, z))
        return pontos

    def gerar_pontos(self, controle: Sequence[Sequence[float]],
                     projetado: Optional[Sequence] = None) -> List[Ponto]:
        controle = [Transform.como_3d(p) for p in controle]
        geometrias_projetadas = self.geometrias(projetado if projetado is not None else controle)
        curva: List[Ponto] = []
        for geometria, geometria_projetada in zip(self.geometrias(controle), geometrias_projetadas):
            n = self.passos(geometria_projetada)
            pontos = self.forward_differences(self.diferencas_iniciais(geometria, n), n)
            curva.extend(pontos[1:] if curva else pontos)
        return curva
