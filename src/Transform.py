import math
from typing import List, Sequence, Tuple

Matriz = List[List[float]]
Ponto = Tuple[float, float]


class Transform:
    """Rotinas de preparo e aplicação de matrizes de transformação 2D
    em coordenadas homogêneas.

    Convenção (vetor-linha, como no material da disciplina):
        [x' y' 1] = [x y 1] · M
    Logo, aplicar M1 e depois M2 equivale a aplicar a matriz M1 · M2.
    """

    # ------------------------------------------------------------------
    # Operações básicas com matrizes
    # ------------------------------------------------------------------
    @staticmethod
    def identidade() -> Matriz:
        return [[1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0]]

    @staticmethod
    def mult_matrix(m1: Matriz, m2: Matriz) -> Matriz:
        rows_m1 = len(m1)
        cols_m1 = len(m1[0])
        cols_m2 = len(m2[0])

        result = [[0.0 for _ in range(cols_m2)] for _ in range(rows_m1)]

        for i in range(rows_m1):
            for j in range(cols_m2):
                for k in range(cols_m1):
                    result[i][j] += m1[i][k] * m2[k][j]

        return result

    @staticmethod
    def compor(*matrizes: Matriz) -> Matriz:
        """Concatena as matrizes na ordem em que devem ser aplicadas."""
        resultado = Transform.identidade()
        for m in matrizes:
            resultado = Transform.mult_matrix(resultado, m)
        return resultado

    # ------------------------------------------------------------------
    # Preparo das matrizes elementares (EQ. 2.4, 2.5 e 2.6)
    # ------------------------------------------------------------------
    @staticmethod
    def matriz_translacao(dx: float, dy: float) -> Matriz:
        return [[1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [dx,  dy,  1.0]]

    @staticmethod
    def matriz_escala(sx: float, sy: float) -> Matriz:
        return [[sx,  0.0, 0.0],
                [0.0, sy,  0.0],
                [0.0, 0.0, 1.0]]

    @staticmethod
    def matriz_rotacao(graus: float) -> Matriz:
        """Rotação anti-horária em torno da origem do mundo."""
        theta = math.radians(graus)
        c, s = math.cos(theta), math.sin(theta)
        return [[c,   s,   0.0],
                [-s,  c,   0.0],
                [0.0, 0.0, 1.0]]

    # ------------------------------------------------------------------
    # Preparo das matrizes compostas (EQ. 2.11 e 2.12)
    # ------------------------------------------------------------------
    @staticmethod
    def matriz_rotacao_ponto(graus: float, ponto: Ponto) -> Matriz:
        """Rotação em torno de um ponto arbitrário: T(-P) · R · T(P)."""
        px, py = ponto
        return Transform.compor(
            Transform.matriz_translacao(-px, -py),
            Transform.matriz_rotacao(graus),
            Transform.matriz_translacao(px, py),
        )

    @staticmethod
    def matriz_escala_natural(sx: float, sy: float, centro: Ponto) -> Matriz:
        """Escalonamento "natural" em torno do centro: T(-C) · S · T(C)."""
        cx, cy = centro
        return Transform.compor(
            Transform.matriz_translacao(-cx, -cy),
            Transform.matriz_escala(sx, sy),
            Transform.matriz_translacao(cx, cy),
        )

    # ------------------------------------------------------------------
    # Centro geométrico (EQ. 2.14)
    # ------------------------------------------------------------------
    @staticmethod
    def centro_geometrico(pontos: Sequence[Ponto]) -> Ponto:
        n = len(pontos)
        cx = sum(p[0] for p in pontos) / n
        cy = sum(p[1] for p in pontos) / n
        return cx, cy

    # ------------------------------------------------------------------
    # Aplicação da matriz (o "engine")
    # ------------------------------------------------------------------
    @staticmethod
    def aplicar_ponto(matriz: Matriz, ponto: Ponto) -> Ponto:
        x, y = ponto
        resultado = Transform.mult_matrix([[x, y, 1.0]], matriz)[0]
        return resultado[0], resultado[1]

    @staticmethod
    def aplicar_pontos(matriz: Matriz, pontos: Sequence[Ponto]) -> List[Ponto]:
        return [Transform.aplicar_ponto(matriz, p) for p in pontos]

    @staticmethod
    def aplicar(matriz: Matriz, obj):
        """Rotina genérica: recebe uma matriz homogênea e um objeto qualquer
        e devolve o objeto após a aplicação da matriz."""
        obj.set_points(Transform.aplicar_pontos(matriz, obj.get_points()))
        return obj
