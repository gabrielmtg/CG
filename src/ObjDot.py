import ObjGrafic

class ObjDot(ObjGrafic):

    def __init__(self, pos_x: float, pos_y: float):
        self.pos_x = pos_x
        self.pos_y = pos_y

    def move_x(self, distance: float):
        self.pos_x = self.pos_x + distance
    
    def move_y(self, distance: float):
        self.pos_y = self.pos_y + distance

    def get_position_x(self):
        return self.pos_x

    def get_position_y(self):
        return self.pos_y
    
    def move_x(self, val):
        ...

    def move_y(self, val):
        ...
 

