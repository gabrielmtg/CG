from src.ObjGrafic import *


class ObjDot(ObjGrafic):

    def __init__(self, canvas: tk.Canvas, name: str, color: str, pos_x: float, pos_y: float):
        super().__init__(canvas, name, color)
        self.x = pos_x
        self.y = pos_y

    def move_right(self, distance: int):
        self.canvas.move(self.id_obj, distance, 0)
        self.x += distance
    
    def move_left(self, distance: int):
        self.canvas.move(self.id_obj, -distance, 0)
        self.x -= distance

    def move_up(self, distance: int):
        self.canvas.move(self.id_obj, 0, -distance)
        self.y -= distance
    
    def move_down(self, distance: int):
        self.canvas.move(self.id_obj, 0, +distance)
        self.y += distance

    def get_position_x(self):
        return self.x

    def get_position_y(self):
        return self.y

    def get_color(self):
        return super().get_color()

    def get_name(self):
        return super().get_name()
 
    def draw(self, radios=2):
        x = self.get_position_x()
        y = self.get_position_y()

        self.id_obj = self.canvas.create_oval(
                    x - radios, y - radios,
                    x + radios, y + radios,
                    fill=self.color, outline=self.color, tags=self.name
                )

    def erase(self):
        if (self.id_obj is not None):
            self.canvas.delete(self.id_obj)
