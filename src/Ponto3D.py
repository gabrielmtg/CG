from typing import Tuple

from src.Transform import Transform, Matriz


class Ponto3D:

    def __init__(self, x: float, y: float, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def coords(self) -> Tuple[float, float, float]:
        return self.x, self.y, self.z

    def set(self, x: float, y: float, z: float = 0.0):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def transformar(self, matriz: Matriz):
        self.x, self.y, self.z = Transform.aplicar_ponto(matriz, self.coords())

    def transladar(self, dx: float, dy: float, dz: float = 0.0):
        self.transformar(Transform.matriz_translacao(dx, dy, dz))

    def escalonar(self, sx: float, sy: float, sz: float = 1.0):
        self.transformar(Transform.matriz_escala(sx, sy, sz))

    def rotacionar_x(self, graus: float):
        self.transformar(Transform.matriz_rotacao_x(graus))

    def rotacionar_y(self, graus: float):
        self.transformar(Transform.matriz_rotacao_y(graus))

    def rotacionar_z(self, graus: float):
        self.transformar(Transform.matriz_rotacao_z(graus))

    def __repr__(self) -> str:
        return f"Ponto3D({self.x:g}, {self.y:g}, {self.z:g})"
