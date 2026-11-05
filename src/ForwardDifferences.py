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

    @staticmethod
    def condicoes_iniciais(coeficientes: Sequence[List[List[float]]], delta_s: float,
                           delta_t: float) -> List[List[List[float]]]:
        e_s = ForwardDifferences.matriz_e(delta_s)
        e_t_transposta = Transform.transposta(ForwardDifferences.matriz_e(delta_t))
        return [Transform.mult_matrix(Transform.mult_matrix(e_s, c), e_t_transposta) for c in coeficientes]

    @staticmethod
    def atualizar_por_linhas(dd: Sequence[List[List[float]]]):
        for matriz in dd:
            for i in range(3):
                matriz[i] = [a + b for a, b in zip(matriz[i], matriz[i + 1])]

    @staticmethod
    def familia_de_curvas(dd: Sequence[List[List[float]]], n_curvas: int, n_pontos: int) -> List[List[Ponto]]:
        curvas = []
        for _ in range(n_curvas):
            primeira_linha = [[matriz[0][j] for matriz in dd] for j in range(4)]
            curvas.append(ForwardDifferences.desenhar_curva(primeira_linha, n_pontos - 1))
            ForwardDifferences.atualizar_por_linhas(dd)
        return curvas

    @staticmethod
    def desenhar_superficie(coeficientes: Sequence[List[List[float]]], n_curvas_s: int, n_curvas_t: int,
                            n_pontos: int) -> Tuple[List[List[Ponto]], List[List[Ponto]]]:
        delta = 1.0 / (n_pontos - 1)
        dd = ForwardDifferences.condicoes_iniciais(coeficientes, 1.0 / (n_curvas_s - 1), delta)
        curvas_em_t = ForwardDifferences.familia_de_curvas(dd, n_curvas_s, n_pontos)
        dd = ForwardDifferences.condicoes_iniciais(coeficientes, delta, 1.0 / (n_curvas_t - 1))
        dd = [Transform.transposta(matriz) for matriz in dd]
        curvas_em_s = ForwardDifferences.familia_de_curvas(dd, n_curvas_t, n_pontos)
        return curvas_em_t, curvas_em_s
