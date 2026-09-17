class Viewport:
    """Transformada de viewport: leva coordenadas normalizadas (SCN, no
    intervalo [-1, 1]) para coordenadas de tela (pixels do canvas)."""

    def __init__(self, vp_xmin: float, vp_ymin: float, vp_xmax: float, vp_ymax: float):
        self.vp_xmin = vp_xmin
        self.vp_ymin = vp_ymin
        self.vp_xmax = vp_xmax
        self.vp_ymax = vp_ymax

    def transform(self, xn: float, yn: float):
        vp_width = self.vp_xmax - self.vp_xmin
        vp_height = self.vp_ymax - self.vp_ymin

        sx = (xn + 1) / 2 * vp_width + self.vp_xmin
        sy = (1 - (yn + 1) / 2) * vp_height + self.vp_ymin
        return sx, sy
