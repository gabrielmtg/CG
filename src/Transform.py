import math
from typing import List, Sequence, Tuple

Matriz = List[List[float]]
Ponto = Tuple[float, float, float]


class Transform:

    @staticmethod
    def identidade() -> Matriz:
        return [[1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]]

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
    def transposta(m: Matriz) -> Matriz:
        return [list(linha) for linha in zip(*m)]

    @staticmethod
    def compor_4x4(a: Matriz, g: Matriz, b: Matriz) -> Matriz:
        return Transform.mult_matrix(Transform.mult_matrix(a, g), b)

    @staticmethod
    def compor(*matrizes: Matriz) -> Matriz:
        resultado = Transform.identidade()
        for m in matrizes:
            resultado = Transform.mult_matrix(resultado, m)
        return resultado

    @staticmethod
    def matriz_translacao(dx: float, dy: float, dz: float = 0.0) -> Matriz:
        return [[1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [dx,  dy,  dz,  1.0]]

    @staticmethod
    def matriz_escala(sx: float, sy: float, sz: float = 1.0) -> Matriz:
        return [[sx,  0.0, 0.0, 0.0],
                [0.0, sy,  0.0, 0.0],
                [0.0, 0.0, sz,  0.0],
                [0.0, 0.0, 0.0, 1.0]]

    @staticmethod
    def matriz_rotacao_x(graus: float) -> Matriz:
        c, s = math.cos(math.radians(graus)), math.sin(math.radians(graus))
        return [[1.0, 0.0, 0.0, 0.0],
                [0.0, c,   s,   0.0],
                [0.0, -s,  c,   0.0],
                [0.0, 0.0, 0.0, 1.0]]

    @staticmethod
    def matriz_rotacao_y(graus: float) -> Matriz:
        c, s = math.cos(math.radians(graus)), math.sin(math.radians(graus))
        return [[c,   0.0, -s,  0.0],
                [0.0, 1.0, 0.0, 0.0],
                [s,   0.0, c,   0.0],
                [0.0, 0.0, 0.0, 1.0]]

    @staticmethod
    def matriz_rotacao_z(graus: float) -> Matriz:
        c, s = math.cos(math.radians(graus)), math.sin(math.radians(graus))
        return [[c,   s,   0.0, 0.0],
                [-s,  c,   0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]]

    @staticmethod
    def matriz_rotacao_ponto(graus: float, ponto: Sequence[float], eixo: str = "z") -> Matriz:
        px, py, pz = Transform.como_3d(ponto)
        rotacao = {"x": Transform.matriz_rotacao_x, "y": Transform.matriz_rotacao_y,
                   "z": Transform.matriz_rotacao_z}[eixo.lower()]
        return Transform.compor(
            Transform.matriz_translacao(-px, -py, -pz),
            rotacao(graus),
            Transform.matriz_translacao(px, py, pz),
        )

    @staticmethod
    def matriz_rotacao_eixo(graus: float, ponto: Sequence[float], direcao: Sequence[float]) -> Matriz:
        px, py, pz = Transform.como_3d(ponto)
        a, b, c = Transform.normalizar(direcao)
        r = math.hypot(b, c)
        theta_x = math.degrees(math.atan2(-c, b))
        theta_z = math.degrees(math.atan2(a, r))
        return Transform.compor(
            Transform.matriz_translacao(-px, -py, -pz),
            Transform.matriz_rotacao_x(theta_x),
            Transform.matriz_rotacao_z(theta_z),
            Transform.matriz_rotacao_y(graus),
            Transform.matriz_rotacao_z(-theta_z),
            Transform.matriz_rotacao_x(-theta_x),
            Transform.matriz_translacao(px, py, pz),
        )

    @staticmethod
    def matriz_escala_natural(sx: float, sy: float, sz: float, centro: Sequence[float]) -> Matriz:
        cx, cy, cz = Transform.como_3d(centro)
        return Transform.compor(
            Transform.matriz_translacao(-cx, -cy, -cz),
            Transform.matriz_escala(sx, sy, sz),
            Transform.matriz_translacao(cx, cy, cz),
        )

    @staticmethod
    def matriz_perspectiva(d: float) -> Matriz:
        return [[1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, -1.0 / d],
                [0.0, 0.0, 0.0, 0.0]]

    @staticmethod
    def aplicar_ponto_homogeneo(matriz: Matriz, ponto: Sequence[float]) -> Ponto:
        x, y, z = Transform.como_3d(ponto)
        X, Y, Z, W = Transform.mult_matrix([[x, y, z, 1.0]], matriz)[0]
        return X / W, Y / W, Z / W

    @staticmethod
    def como_3d(p: Sequence[float]) -> Ponto:
        return (float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0)

    @staticmethod
    def centro_geometrico(pontos: Sequence[Sequence[float]]) -> Ponto:
        pontos = [Transform.como_3d(p) for p in pontos]
        n = len(pontos)
        return (sum(p[0] for p in pontos) / n,
                sum(p[1] for p in pontos) / n,
                sum(p[2] for p in pontos) / n)

    @staticmethod
    def aplicar_ponto(matriz: Matriz, ponto: Sequence[float]) -> Ponto:
        x, y, z = Transform.como_3d(ponto)
        resultado = Transform.mult_matrix([[x, y, z, 1.0]], matriz)[0]
        return resultado[0], resultado[1], resultado[2]

    @staticmethod
    def aplicar_vetor(matriz: Matriz, vetor: Sequence[float]) -> Ponto:
        x, y, z = Transform.como_3d(vetor)
        resultado = Transform.mult_matrix([[x, y, z, 0.0]], matriz)[0]
        return resultado[0], resultado[1], resultado[2]

    @staticmethod
    def aplicar_pontos(matriz: Matriz, pontos: Sequence[Sequence[float]]) -> List[Ponto]:
        return [Transform.aplicar_ponto(matriz, p) for p in pontos]

    @staticmethod
    def aplicar(matriz: Matriz, obj):
        for p in obj.points:
            p.transformar(matriz)
        return obj

    @staticmethod
    def norma(v: Sequence[float]) -> float:
        return math.sqrt(sum(c * c for c in Transform.como_3d(v)))

    @staticmethod
    def normalizar(v: Sequence[float]) -> Ponto:
        x, y, z = Transform.como_3d(v)
        n = math.sqrt(x * x + y * y + z * z)
        if n == 0:
            raise ValueError("Vetor nulo não pode ser normalizado.")
        return x / n, y / n, z / n

    @staticmethod
    def escalar(a: Sequence[float], b: Sequence[float]) -> float:
        a, b = Transform.como_3d(a), Transform.como_3d(b)
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    @staticmethod
    def vetorial(a: Sequence[float], b: Sequence[float]) -> Ponto:
        (ax, ay, az), (bx, by, bz) = Transform.como_3d(a), Transform.como_3d(b)
        return ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
