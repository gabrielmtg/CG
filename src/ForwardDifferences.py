from typing import List, Sequence, Tuple

from src.Transform import Transform

Ponto = Tuple[float, float, float]


class ForwardDifferences:

    @staticmethod
    def matriz_e(delta: float) -> List[List[float]]:
        d1, d2, d3 = delta, delta ** 2, delta ** 3
        return [[0.0,     0.0,     0.0, 1.0],
                [d3,      d2,      d1,  0.0],
                [6 * d3,  2 * d2,  0.0, 0.0],
                [6 * d3,  0.0,     0.0, 0.0]]

    @staticmethod
    def diferencas_iniciais(coeficientes: Sequence[Sequence[float]], passos: int) -> List[List[float]]:
        return Transform.mult_matrix(ForwardDifferences.matriz_e(1.0 / passos), [list(c) for c in coeficientes])

    @staticmethod
    def desenhar_curva(diferencas: List[List[float]], passos: int) -> List[Ponto]:
        (x, y, z), (dx, dy, dz), (d2x, d2y, d2z), (d3x, d3y, d3z) = diferencas
        pontos = [(x, y, z)]
        for _ in range(passos):
            x, dx, d2x = x + dx, dx + d2x, d2x + d3x
            y, dy, d2y = y + dy, dy + d2y, d2y + d3y
            z, dz, d2z = z + dz, dz + d2z, d2z + d3z
            pontos.append((x, y, z))
        return pontos
