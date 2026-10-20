import math
from abc import abstractmethod
from typing import List, Optional, Sequence, Tuple

from src.Clipping import Clipping
from src.ObjGrafic import ObjGrafic

Ponto = Tuple[float, float, float]


class ObjCurvaParametrica(ObjGrafic):
    PASSOS_MIN = 10
    PASSOS_MAX = 300

    def __init__(self, canvas, name: str, color: str, tipo: str, points: Sequence[Sequence[float]]):
        super().__init__(canvas, name, color, tipo, points)
        self.scn_curva: List[Optional[Tuple[float, float]]] = []

    @staticmethod
    def passos(geometria_projetada: Sequence[Optional[Sequence[float]]]) -> int:
        pontos = [p for p in geometria_projetada if p is not None]
        if len(pontos) < len(geometria_projetada):
            return ObjCurvaParametrica.PASSOS_MAX
        comprimento = sum(math.dist(pontos[i][:2], pontos[i + 1][:2]) for i in range(len(pontos) - 1))
        return max(ObjCurvaParametrica.PASSOS_MIN, min(ObjCurvaParametrica.PASSOS_MAX, int(comprimento * 100)))

    @abstractmethod
    def gerar_pontos(self, controle: Sequence[Sequence[float]],
                     projetado: Optional[Sequence[Optional[Sequence[float]]]] = None) -> List[Ponto]:
        pass

    def update_scn(self, projetar):
        super().update_scn(projetar)
        self.scn_curva = [projetar(p) for p in self.gerar_pontos(self.get_points(), self.scn_points)]

    def draw(self, clipping: Clipping, transform):
        self.erase()
        self.desenhar_curva_recortada(self.scn_curva, clipping, transform)
