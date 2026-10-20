import math
from typing import Callable, Optional, Sequence, Tuple

from src.Transform import Transform, Matriz, Ponto

Projetor = Callable[[Sequence[float]], Optional[Tuple[float, float]]]


class Window:
    PARALELA = "Paralela"
    PERSPECTIVA = "Perspectiva"
    PROJECOES = (PARALELA, PERSPECTIVA)
    DISTANCIA_MINIMA_COP = 1e-3

    def __init__(self, vrp: Sequence[float], width: float, height: float,
                 vpn: Sequence[float] = (0.0, 0.0, 1.0), vup: Sequence[float] = (0.0, 1.0, 0.0),
                 projecao: str = PARALELA, distancia_cop: float = 1000.0):
        self.vrp = Transform.como_3d(vrp)
        self.width = width
        self.height = height
        self.vpn = Transform.normalizar(vpn)
        self.vup = self._ortogonalizar(vup)
        self.projecao = projecao
        self.distancia_cop = distancia_cop
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

    def get_cop(self) -> Ponto:
        return tuple(self.vrp[i] + self.distancia_cop * self.vpn[i] for i in range(3))

    def set_projecao(self, projecao: str):
        if projecao not in self.PROJECOES:
            raise ValueError(f"Projeção desconhecida: {projecao}")
        self.projecao = projecao

    def set_distancia_cop(self, d: float):
        if d <= 0:
            raise ValueError("A distância do COP ao plano de projeção deve ser positiva.")
        self.distancia_cop = d

    def campo_de_visao(self) -> float:
        return math.degrees(2 * math.atan(self.width / (2 * self.distancia_cop)))

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

    def matriz_alinhamento(self, origem: Sequence[float]) -> Matriz:
        theta_x, theta_y = self.angulos_vpn()
        return Transform.compor(
            Transform.matriz_translacao(-origem[0], -origem[1], -origem[2]),
            Transform.matriz_rotacao_x(theta_x),
            Transform.matriz_rotacao_y(theta_y),
        )

    def matriz_projecao(self) -> Matriz:
        return self.matriz_alinhamento(self.vrp)

    def angulo_vup(self, matriz_projecao: Matriz) -> float:
        vx, vy, _ = Transform.aplicar_vetor(matriz_projecao, self.vup)
        return math.degrees(math.atan2(vx, vy))

    def matriz_normalizacao(self, matriz_projecao: Matriz) -> Matriz:
        return Transform.compor(
            Transform.matriz_rotacao_z(self.angulo_vup(matriz_projecao)),
            Transform.matriz_escala(2.0 / self.width, 2.0 / self.height, 1.0),
        )

    def matriz_scn(self) -> Matriz:
        projecao = self.matriz_projecao()
        return Transform.compor(projecao, self.matriz_normalizacao(projecao))

    def projetor(self) -> Projetor:
        if self.projecao == self.PERSPECTIVA:
            return self._projetor_perspectiva()
        matriz_scn = self.matriz_scn()

        def projetar_paralela(p):
            x, y, _ = Transform.aplicar_ponto(matriz_scn, p)
            return x, y
        return projetar_paralela

    def _projetor_perspectiva(self) -> Projetor:
        alinhamento = self.matriz_alinhamento(self.get_cop())
        mper = Transform.matriz_perspectiva(self.distancia_cop)
        normalizacao = self.matriz_normalizacao(alinhamento)
        limite = -self.DISTANCIA_MINIMA_COP * self.distancia_cop

        def projetar_perspectiva(p):
            x, y, z = Transform.aplicar_ponto(alinhamento, p)
            if z >= limite:
                return None
            xp, yp, _ = Transform.aplicar_ponto_homogeneo(mper, (x, y, z))
            xn, yn, _ = Transform.aplicar_ponto(normalizacao, (xp, yp, 0.0))
            return xn, yn
        return projetar_perspectiva
