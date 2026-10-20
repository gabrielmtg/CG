import tkinter as tk
from typing import List, Optional, Sequence, Tuple

from src.ObjCurvaParametrica import ObjCurvaParametrica
from src.Transform import Transform

Ponto = Tuple[float, float, float]


class ObjCurva(ObjCurvaParametrica):
    MATRIZ_BEZIER = [[-1.0,  3.0, -3.0, 1.0],
                     [3.0, -6.0,  3.0, 0.0],
                     [-3.0,  3.0,  0.0, 0.0],
                     [1.0,  0.0,  0.0, 0.0]]

    def __init__(self, canvas: tk.Canvas, name: str, color: str, points: Sequence[Sequence[float]]):
        super().__init__(canvas, name, color, "curva", points)

    @staticmethod
    def quantidade_valida(n: int) -> bool:
        return n >= 4 and (n - 1) % 3 == 0

    @staticmethod
    def segmentos(controle: Sequence) -> List[list]:
        return [list(controle[i:i + 4]) for i in range(0, len(controle) - 3, 3)]

    @staticmethod
    def blending(t: float) -> List[float]:
        return Transform.mult_matrix([[t ** 3, t ** 2, t, 1.0]], ObjCurva.MATRIZ_BEZIER)[0]

    @staticmethod
    def ponto_bezier(t: float, geometria: Sequence[Sequence[float]]) -> Tuple[float, ...]:
        b = ObjCurva.blending(t)
        return tuple(sum(b[j] * geometria[j][k] for j in range(4)) for k in range(len(geometria[0])))

    def gerar_pontos(self, controle: Sequence[Sequence[float]],
                     projetado: Optional[Sequence] = None) -> List[Ponto]:
        controle = [Transform.como_3d(p) for p in controle]
        segmentos_projetados = self.segmentos(projetado if projetado is not None else controle)
        curva: List[Ponto] = []
        for geometria, geometria_projetada in zip(self.segmentos(controle), segmentos_projetados):
            n = self.passos(geometria_projetada)
            inicio = 1 if curva else 0
            for i in range(inicio, n + 1):
                curva.append(self.ponto_bezier(i / n, geometria))
        return curva
