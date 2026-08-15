import tkinter as tk
from src.ObjGrafic import ObjGrafic

class ObjLine(ObjGrafic):

    def __init__(self,canvas: tk.Canvas, name: str, color: str, x0: float, y0: float, x1: float, y1: float):
        super().__init__(canvas, name, color)
        self.point0 = [x0, y0]
        self.point1 = [x1, y1]
        self.points = [self.point0, self.point1]

    def move_line_x(self, distance: float):
        self.canvas.move(self.id_obj, distance, 0)
        for i in self.points:
            i[0] = i[0] + distance

    def move_line_y(self, distance: float):
        self.canvas.move(self.id_obj, 0, distance)
        for i in self.points:
            i[1] = i[1] + distance    

    def move_right(self, distance: int):
        self.canvas.move(self.id_obj, distance, 0)
        for i in self.points:
            i[0] += distance
    
    def move_left(self, distance: int):
        self.canvas.move(self.id_obj, -distance, 0)
        for i in self.points:
            i[0] -= distance

    def move_up(self, distance: int):
        self.canvas.move(self.id_obj, 0, -distance)
        for i in self.points:
            i[1] -= distance

    def move_down(self, distance: int):
        self.canvas.move(self.id_obj, 0, distance)
        for i in self.points:
            i[1] += distance

    def move_point(self, point: int, distance: int, direction: str):
        if (point not in [0, 1]):
            return
        
        if (direction == "x"):
            self.points[point][0] += distance

        if (direction == "y"):
            self.points[point][1] += distance

        self.erase()
        self.draw()

    def get_point0_x(self):
        return self.point0[0]

    def get_point0_y(self):
        return self.point0[1]

    def get_point1_x(self):
        return self.point1[0]

    def get_point1_y(self):
        return self.point1[1]

    def get_color(self):
        return super().get_color()

    def get_name(self):
        return super().get_name()

    def draw(self):
        x0, y0 = self.points[0]
        x1, y1 = self.points[1]

        self.id_obj = self.canvas.create_line(x0, y0, x1, y1, fill=self.color, tags=self.name, width=3)

    def erase(self):
        if (self.id_obj is not None):
            self.canvas.delete(self.id_obj)
