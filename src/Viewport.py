class Viewport:

    def __init__(self, vp_xmin: float, vp_ymin: float, vp_xmax: float, vp_ymax: float,
                 w_xmin: float, w_ymin: float, w_xmax: float, w_ymax: float):
        self.vp_xmin = vp_xmin
        self.vp_ymin = vp_ymin
        self.vp_xmax = vp_xmax
        self.vp_ymax = vp_ymax
        self.w_xmin = w_xmin
        self.w_ymin = w_ymin
        self.w_xmax = w_xmax
        self.w_ymax = w_ymax

    def transform(self, x: float, y: float):
        w_width = self.w_xmax - self.w_xmin
        w_height = self.w_ymax - self.w_ymin
        vp_width = self.vp_xmax - self.vp_xmin
        vp_height = self.vp_ymax - self.vp_ymin

        sx = (x - self.w_xmin) / w_width * vp_width + self.vp_xmin
        sy = (1 - (y - self.w_ymin) / w_height) * vp_height + self.vp_ymin
        return sx, sy

    def pan(self, dx: float, dy: float):
        self.w_xmin += dx
        self.w_xmax += dx
        self.w_ymin += dy
        self.w_ymax += dy

    def zoom(self, factor: float):
        cx = (self.w_xmin + self.w_xmax) / 2
        cy = (self.w_ymin + self.w_ymax) / 2
        half_w = (self.w_xmax - self.w_xmin) / (2 * factor)
        half_h = (self.w_ymax - self.w_ymin) / (2 * factor)
        self.w_xmin = cx - half_w
        self.w_xmax = cx + half_w
        self.w_ymin = cy - half_h
        self.w_ymax = cy + half_h
