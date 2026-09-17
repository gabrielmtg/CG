from src.Transform import Transform, Matriz, Ponto


class Window:

    def __init__(self, cx: float, cy: float, width: float, height: float, angle: float = 0.0):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.angle = angle

    def get_center(self) -> Ponto:
        return self.cx, self.cy

    def get_angle(self) -> float:
        return self.angle

    def to_world_vector(self, dx: float, dy: float) -> Ponto:
        return Transform.aplicar_ponto(Transform.matriz_rotacao(self.angle), (dx, dy))

    def pan(self, dx: float, dy: float):
        wx, wy = self.to_world_vector(dx, dy)
        self.cx += wx
        self.cy += wy

    def zoom(self, factor: float):
        self.width /= factor
        self.height /= factor

    def rotate(self, graus: float):
        self.angle = (self.angle + graus) % 360

    def matriz_scn(self) -> Matriz:
        return Transform.compor(
            Transform.matriz_translacao(-self.cx, -self.cy),
            Transform.matriz_rotacao(-self.angle),
            Transform.matriz_escala(2.0 / self.width, 2.0 / self.height),
        )
