import math
from typing import Sequence, Tuple

from src.Transform import Transform, Matriz, Ponto


class Window:

    def __init__(self, vrp: Sequence[float], width: float, height: float,
                 vpn: Sequence[float] = (0.0, 0.0, 1.0), vup: Sequence[float] = (0.0, 1.0, 0.0)):
        self.vrp = Transform.como_3d(vrp)
        self.width = width
        self.height = height
        self.vpn = Transform.normalizar(vpn)
        self.vup = self._ortogonalizar(vup)
        self._inicial = (self.vrp, width, height, self.vpn, self.vup)

    def _ortogonalizar(self, vup: Sequence[float]) -> Ponto:
        proj = Transform.escalar(vup, self.vpn)
        return Transform.normalizar([vup[i] - proj * self.vpn[i] for i in range(3)])

    def get_center(self) -> Ponto:
        return self.vrp

    def get_vpn(self) -> Ponto:
        return self.vpn

    def get_vup(self) -> Ponto:
        return self.vup

    def eixos(self) -> Tuple[Ponto, Ponto, Ponto]:
        n = self.vpn
        u = Transform.normalizar(Transform.vetorial(self.vup, n))
        v = Transform.vetorial(n, u)
        return u, v, n

    def to_world_vector(self, dx: float, dy: float, dz: float = 0.0) -> Ponto:
        u, v, n = self.eixos()
        return tuple(dx * u[i] + dy * v[i] + dz * n[i] for i in range(3))

    def pan(self, dx: float, dy: float, dz: float = 0.0):
        w = self.to_world_vector(dx, dy, dz)
        self.vrp = tuple(self.vrp[i] + w[i] for i in range(3))

    def zoom(self, factor: float):
        self.width /= factor
        self.height /= factor

    def _girar(self, graus: float, eixo: Sequence[float]):
        m = Transform.matriz_rotacao_eixo(graus, (0.0, 0.0, 0.0), eixo)
        self.vpn = Transform.normalizar(Transform.aplicar_vetor(m, self.vpn))
        self.vup = self._ortogonalizar(Transform.aplicar_vetor(m, self.vup))

    def rotate(self, graus: float):
        self._girar(graus, self.eixos()[2])

    def rotate_x(self, graus: float):
        self._girar(graus, self.eixos()[0])

    def rotate_y(self, graus: float):
        self._girar(graus, self.eixos()[1])

    def resetar(self):
        self.vrp, self.width, self.height, self.vpn, self.vup = self._inicial

    def angulos_vpn(self) -> Tuple[float, float]:
        a, b, c = self.vpn
        theta_x = math.degrees(math.atan2(b, c))
        theta_y = math.degrees(math.atan2(-a, math.hypot(b, c)))
        return theta_x, theta_y

    def matriz_projecao(self) -> Matriz:
        theta_x, theta_y = self.angulos_vpn()
        return Transform.compor(
            Transform.matriz_translacao(-self.vrp[0], -self.vrp[1], -self.vrp[2]),
            Transform.matriz_rotacao_x(theta_x),
            Transform.matriz_rotacao_y(theta_y),
        )

    def angulo_vup(self, matriz_projecao: Matriz) -> float:
        vx, vy, _ = Transform.aplicar_vetor(matriz_projecao, self.vup)
        return math.degrees(math.atan2(vx, vy))

    def matriz_scn(self) -> Matriz:
        projecao = self.matriz_projecao()
        return Transform.compor(
            projecao,
            Transform.matriz_rotacao_z(self.angulo_vup(projecao)),
            Transform.matriz_escala(2.0 / self.width, 2.0 / self.height, 1.0),
        )
