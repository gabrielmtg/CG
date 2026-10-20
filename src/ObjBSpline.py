import tkinter as tk
from typing import List, Optional, Sequence, Tuple

from src.ForwardDifferences import ForwardDifferences
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
    def diferencas_iniciais(geometria: Sequence[Sequence[float]], passos: int) -> List[List[float]]:
        return ForwardDifferences.diferencas_iniciais(ObjBSpline.coeficientes(geometria), passos)

    @staticmethod
    def forward_differences(diferencas: List[List[float]], passos: int) -> List[Ponto]:
        return ForwardDifferences.desenhar_curva(diferencas, passos)

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
