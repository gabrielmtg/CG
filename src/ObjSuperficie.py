import math
import tkinter as tk
from typing import List, Optional, Sequence, Tuple

from src.Clipping import Clipping
from src.ForwardDifferences import ForwardDifferences
from src.ObjCurva import ObjCurva
from src.ObjGrafic import ObjGrafic
from src.Ponto3D import Ponto3D
from src.Transform import Transform, Matriz

Ponto = Tuple[float, float, float]


class ObjSuperficie(ObjGrafic):
    MATRIZ_BEZIER = ObjCurva.MATRIZ_BEZIER
    DIVISOES = 10
    PASSOS_MIN = 8
    PASSOS_MAX = 64
    LARGURA_LINHA = 1

    def __init__(self, canvas: tk.Canvas, name: str, color: str,
                 vertices: Sequence[Sequence[float]], retalhos: Sequence[Sequence[Sequence[int]]]):
        super().__init__(canvas, name, color, "superficie", vertices)
        if not retalhos:
            raise ValueError("A superfície precisa de ao menos um retalho.")
        for retalho in retalhos:
            if len(retalho) != 4 or any(len(linha) != 4 for linha in retalho):
                raise ValueError("Cada retalho deve ser uma matriz de geometria 4 x 4.")
            if any(not 0 <= i < len(self.points) for linha in retalho for i in linha):
                raise ValueError("Retalho usa um ponto de controle inexistente.")
        self.retalhos: List[List[List[Ponto3D]]] = [
            [[self.points[i] for i in linha] for linha in retalho] for retalho in retalhos
        ]
        self.scn_linhas: List[List[Optional[Tuple[float, float]]]] = []

    @classmethod
    def de_matriz(cls, canvas: tk.Canvas, name: str, color: str,
                  matriz: Sequence[Sequence[Sequence[float]]]) -> "ObjSuperficie":
        linhas, colunas = len(matriz), len(matriz[0]) if matriz else 0
        if linhas < 4 or linhas % 4 or colunas < 4 or colunas % 4 or any(len(l) != colunas for l in matriz):
            raise ValueError("A matriz de pontos de controle deve ter 4, 8, 12, ... linhas e "
                             "4, 8, 12, ... pontos em todas as linhas (cada bloco 4 x 4 é um retalho).")
        vertices: List[Ponto] = []
        indice = {}

        def indice_de(p):
            p = Transform.como_3d(p)
            if p not in indice:
                indice[p] = len(vertices)
                vertices.append(p)
            return indice[p]

        retalhos = []
        for a in range(0, linhas, 4):
            for b in range(0, colunas, 4):
                retalhos.append([[indice_de(matriz[a + i][b + j]) for j in range(4)] for i in range(4)])
        return cls(canvas, name, color, vertices, retalhos)

    def get_retalhos(self) -> List[List[List[int]]]:
        indice = {id(p): i for i, p in enumerate(self.points)}
        return [[[indice[id(p)] for p in linha] for linha in retalho] for retalho in self.retalhos]

    @staticmethod
    def coeficientes(geometria: Sequence[Sequence[Sequence[float]]]) -> List[Matriz]:
        m, mt = ObjSuperficie.MATRIZ_BEZIER, Transform.transposta(ObjSuperficie.MATRIZ_BEZIER)
        return [Transform.compor_4x4(m, [[p[k] for p in linha] for linha in geometria], mt) for k in range(3)]

    @staticmethod
    def potencias(u: float) -> List[float]:
        return [u ** 3, u ** 2, u, 1.0]

    @staticmethod
    def ponto(coeficientes: Sequence[Matriz], s: float, t: float) -> Ponto:
        S, T = ObjSuperficie.potencias(s), ObjSuperficie.potencias(t)
        return tuple(sum(S[i] * c[i][j] * T[j] for i in range(4) for j in range(4)) for c in coeficientes)

    @staticmethod
    def curva_em_s(coeficientes: Sequence[Matriz], t: float) -> List[List[float]]:
        T = ObjSuperficie.potencias(t)
        return [[sum(c[i][j] * T[j] for j in range(4)) for c in coeficientes] for i in range(4)]

    @staticmethod
    def curva_em_t(coeficientes: Sequence[Matriz], s: float) -> List[List[float]]:
        S = ObjSuperficie.potencias(s)
        return [[sum(S[i] * c[i][j] for i in range(4)) for c in coeficientes] for j in range(4)]

    @staticmethod
    def passos(geometria_projetada: Sequence[Sequence[Optional[Sequence[float]]]]) -> int:
        pontos = [p for linha in geometria_projetada for p in linha]
        if any(p is None for p in pontos):
            return ObjSuperficie.PASSOS_MAX
        bordas = [geometria_projetada[0], geometria_projetada[3],
                  [linha[0] for linha in geometria_projetada], [linha[3] for linha in geometria_projetada]]
        comprimento = max(sum(math.dist(b[i], b[i + 1]) for i in range(3)) for b in bordas)
        return max(ObjSuperficie.PASSOS_MIN, min(ObjSuperficie.PASSOS_MAX, int(comprimento * 40)))

    def gerar_linhas(self, geometria: Sequence[Sequence[Sequence[float]]], passos: int) -> List[List[Ponto]]:
        coeficientes = self.coeficientes(geometria)
        linhas = []
        for k in range(self.DIVISOES + 1):
            u = k / self.DIVISOES
            for coef_curva in (self.curva_em_s(coeficientes, u), self.curva_em_t(coeficientes, u)):
                diferencas = ForwardDifferences.diferencas_iniciais(coef_curva, passos)
                linhas.append(ForwardDifferences.desenhar_curva(diferencas, passos))
        return linhas

    def update_scn(self, projetar):
        super().update_scn(projetar)
        projetado = {id(p): q for p, q in zip(self.points, self.scn_points)}
        self.scn_linhas = []
        for retalho in self.retalhos:
            geometria = [[p.coords() for p in linha] for linha in retalho]
            passos = self.passos([[projetado[id(p)] for p in linha] for linha in retalho])
            for linha in self.gerar_linhas(geometria, passos):
                self.scn_linhas.append([projetar(p) for p in linha])

    def draw(self, clipping: Clipping, transform):
        self.erase()
        for linha in self.scn_linhas:
            self.desenhar_polilinha_recortada(linha, clipping, transform, self.LARGURA_LINHA)
