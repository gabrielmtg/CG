import math
import tkinter as tk
from typing import List, Sequence

from src.ForwardDifferences import ForwardDifferences
from src.ObjBSpline import ObjBSpline
from src.ObjSuperficie import ObjSuperficie, Ponto
from src.Transform import Matriz


class ObjSuperficieBSpline(ObjSuperficie):
    MATRIZ = ObjBSpline.MATRIZ_BSPLINE
    DIMENSAO_MIN = 4
    DIMENSAO_MAX = 20

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 vertices: Sequence[Sequence[float]], matriz: Sequence[Sequence[int]]):
        self.validar_dimensoes(matriz)
        super().__init__(canvas, name, color, "superficie_bspline", vertices, self.submatrizes(matriz))
        self.matriz = [list(linha) for linha in matriz]
        self.retalhos_em_s = len(matriz) - 3
        self.retalhos_em_t = len(matriz[0]) - 3

    @classmethod
    def validar_dimensoes(cls, matriz: Sequence[Sequence]):
        colunas = len(matriz[0]) if matriz else 0
        if (not cls.DIMENSAO_MIN <= len(matriz) <= cls.DIMENSAO_MAX
                or not cls.DIMENSAO_MIN <= colunas <= cls.DIMENSAO_MAX
                or any(len(linha) != colunas for linha in matriz)):
            raise ValueError(f"A matriz de pontos de controle deve ter de {cls.DIMENSAO_MIN} a {cls.DIMENSAO_MAX} "
                             f"linhas, com a mesma quantidade (de {cls.DIMENSAO_MIN} a {cls.DIMENSAO_MAX}) "
                             "de pontos em todas as linhas.")

    @classmethod
    def de_matriz(cls, canvas: tk.Canvas, name: str, color: str,
                  matriz: Sequence[Sequence[Sequence[float]]]) -> "ObjSuperficieBSpline":
        cls.validar_dimensoes(matriz)
        vertices, indices = cls.indexar_matriz(matriz)
        return cls(canvas, name, color, vertices, indices)

    @staticmethod
    def submatrizes(matriz: Sequence[Sequence]) -> List[List[list]]:
        return [[list(linha[b:b + 4]) for linha in matriz[a:a + 4]]
                for a in range(len(matriz) - 3) for b in range(len(matriz[0]) - 3)]

    def get_matriz(self) -> List[List[int]]:
        return [list(linha) for linha in self.matriz]

    def gerar_linhas(self, indice: int, coeficientes: Sequence[Matriz], passos: int) -> List[List[Ponto]]:
        a, b = divmod(indice, self.retalhos_em_t)
        n_curvas_s = math.ceil(self.DIVISOES / self.retalhos_em_s) + 1
        n_curvas_t = math.ceil(self.DIVISOES / self.retalhos_em_t) + 1
        curvas_em_t, curvas_em_s = ForwardDifferences.desenhar_superficie(
            coeficientes, n_curvas_s, n_curvas_t, passos + 1)
        if a < self.retalhos_em_s - 1:
            curvas_em_t = curvas_em_t[:-1]
        if b < self.retalhos_em_t - 1:
            curvas_em_s = curvas_em_s[:-1]
        return curvas_em_t + curvas_em_s
