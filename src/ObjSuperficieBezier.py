import tkinter as tk
from typing import List, Sequence

from src.ObjCurva import ObjCurva
from src.ObjSuperficie import ObjSuperficie, Ponto
from src.Transform import Matriz


class ObjSuperficieBezier(ObjSuperficie):
    MATRIZ = ObjCurva.MATRIZ_BEZIER

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 vertices: Sequence[Sequence[float]], retalhos: Sequence[Sequence[Sequence[int]]]):
        super().__init__(canvas, name, color, "superficie_bezier", vertices, retalhos)

    @classmethod
    def de_matriz(cls, canvas: tk.Canvas, name: str, color: str,
                  matriz: Sequence[Sequence[Sequence[float]]]) -> "ObjSuperficieBezier":
        linhas, colunas = len(matriz), len(matriz[0]) if matriz else 0
        if linhas < 4 or linhas % 4 or colunas < 4 or colunas % 4 or any(len(l) != colunas for l in matriz):
            raise ValueError("A matriz de pontos de controle deve ter 4, 8, 12, ... linhas e "
                             "4, 8, 12, ... pontos em todas as linhas (cada bloco 4 x 4 é um retalho).")
        vertices, indices = cls.indexar_matriz(matriz)
        retalhos = [[indices[a + i][b:b + 4] for i in range(4)]
                    for a in range(0, linhas, 4) for b in range(0, colunas, 4)]
        return cls(canvas, name, color, vertices, retalhos)

    def gerar_linhas(self, indice: int, coeficientes: Sequence[Matriz], passos: int) -> List[List[Ponto]]:
        linhas = []
        for k in range(self.DIVISOES + 1):
            u = k / self.DIVISOES
            linhas.append([self.ponto(coeficientes, i / passos, u) for i in range(passos + 1)])
            linhas.append([self.ponto(coeficientes, u, i / passos) for i in range(passos + 1)])
        return linhas
