from src.Transform import Transform, Matriz, Ponto


class Window:
    """Janela de visualização (window) em coordenadas do mundo (WC).

    A window é tratada como um objeto gráfico qualquer: tem um centro, um
    tamanho e um ângulo de rotação θ em torno do próprio centro.

    A descrição dos objetos no Sistema de Coordenadas Normalizado (SCN) é
    uma mudança de coordenadas do sistema do mundo (xy) para o sistema da
    window (x'y'):
        1. translação da origem para o centro da window  (x' = x - a, y' = y - b)
        2. rotação dos eixos por θ, ou seja, os pontos giram por -θ
           (matriz de rotação de eixos R(-θ): o mundo gira ao contrário da window)
        3. escala para o intervalo [-1, 1] em ambos os eixos
    """

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
        """Converte um deslocamento dado no referencial do usuário (eixos da
        window, onde "para cima" é o cima da tela) para um vetor em WC."""
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
        """Matriz que leva coordenadas do mundo (WC) para o SCN."""
        return Transform.compor(
            Transform.matriz_translacao(-self.cx, -self.cy),
            Transform.matriz_rotacao(-self.angle),
            Transform.matriz_escala(2.0 / self.width, 2.0 / self.height),
        )
