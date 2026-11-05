import math
import tkinter as tk
from abc import abstractmethod
from typing import Dict, List, Optional, Sequence, Tuple

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic
from src.Ponto3D import Ponto3D
from src.Transform import Transform, Matriz

Ponto = Tuple[float, float, float]


class ObjSuperficie(ObjGrafic):
    MATRIZ: Matriz = []
    DIVISOES = 10
    PASSOS_MIN = 8
    PASSOS_MAX = 64
    LARGURA_LINHA = 1

    def __init__(self, canvas: tk.Canvas, name: str, color: str, tipo: str,
                 vertices: Sequence[Sequence[float]], retalhos: Sequence[Sequence[Sequence[int]]]):
        super().__init__(canvas, name, color, tipo, vertices)
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
        self._coordenadas: Optional[List[Ponto]] = None
        self._linhas_por_retalho: Dict[int, Tuple[int, List[List[Ponto]]]] = {}

    @staticmethod
    def indexar_matriz(matriz: Sequence[Sequence[Sequence[float]]]) -> Tuple[List[Ponto], List[List[int]]]:
        vertices: List[Ponto] = []
        indice: Dict[Ponto, int] = {}
        indices = []
        for linha in matriz:
            indices_linha = []
            for p in linha:
                p = Transform.como_3d(p)
                if p not in indice:
                    indice[p] = len(vertices)
                    vertices.append(p)
                indices_linha.append(indice[p])
            indices.append(indices_linha)
        return vertices, indices

    def get_retalhos(self) -> List[List[List[int]]]:
        indice = {id(p): i for i, p in enumerate(self.points)}
        return [[[indice[id(p)] for p in linha] for linha in retalho] for retalho in self.retalhos]

    @classmethod
    def coeficientes(cls, geometria: Sequence[Sequence[Sequence[float]]]) -> List[Matriz]:
        m, mt = cls.MATRIZ, Transform.transposta(cls.MATRIZ)
        return [Transform.compor_4x4(m, [[p[k] for p in linha] for linha in geometria], mt) for k in range(3)]

    @staticmethod
    def potencias(u: float) -> List[float]:
        return [u ** 3, u ** 2, u, 1.0]

    @staticmethod
    def ponto(coeficientes: Sequence[Matriz], s: float, t: float) -> Ponto:
        S, T = ObjSuperficie.potencias(s), ObjSuperficie.potencias(t)
        return tuple(sum(S[i] * c[i][j] * T[j] for i in range(4) for j in range(4)) for c in coeficientes)

    @staticmethod
    def passos(geometria_projetada: Sequence[Sequence[Optional[Sequence[float]]]]) -> int:
        pontos = [p for linha in geometria_projetada for p in linha]
        if any(p is None for p in pontos):
            return ObjSuperficie.PASSOS_MAX
        bordas = [geometria_projetada[0], geometria_projetada[3],
                  [linha[0] for linha in geometria_projetada], [linha[3] for linha in geometria_projetada]]
        comprimento = max(sum(math.dist(b[i], b[i + 1]) for i in range(3)) for b in bordas)
        return max(ObjSuperficie.PASSOS_MIN, min(ObjSuperficie.PASSOS_MAX, int(comprimento * 40)))

    @abstractmethod
    def gerar_linhas(self, indice: int, coeficientes: Sequence[Matriz], passos: int) -> List[List[Ponto]]:
        pass

    def linhas_do_retalho(self, indice: int, passos: int) -> List[List[Ponto]]:
        em_cache = self._linhas_por_retalho.get(indice)
        if em_cache is None or em_cache[0] != passos:
            geometria = [[p.coords() for p in linha] for linha in self.retalhos[indice]]
            em_cache = (passos, self.gerar_linhas(indice, self.coeficientes(geometria), passos))
            self._linhas_por_retalho[indice] = em_cache
        return em_cache[1]

    def update_scn(self, projetar):
        super().update_scn(projetar)
        coordenadas = self.get_points()
        if coordenadas != self._coordenadas:
            self._coordenadas = coordenadas
            self._linhas_por_retalho = {}
        projetado = {id(p): q for p, q in zip(self.points, self.scn_points)}
        self.scn_linhas = []
        for indice, retalho in enumerate(self.retalhos):
            passos = self.passos([[projetado[id(p)] for p in linha] for linha in retalho])
            for linha in self.linhas_do_retalho(indice, passos):
                self.scn_linhas.append([projetar(p) for p in linha])

    def draw(self, clipping: Clipping, transform):
        self.erase()
        for linha in self.scn_linhas:
            self.desenhar_polilinha_recortada(linha, clipping, transform, self.LARGURA_LINHA)
