import ObjGrafic

class ObjLine(ObjGrafic):

    def __init__(self, initial_pos_x: float, initial_pos_y: float, final_pos_x: float, final_pos_y: float):
        self.initial_cord = [initial_pos_x, initial_pos_y]
        self.final_cord = [final_pos_x, final_pos_y]
        self.cords = [self.initial_cord, self.final_cord]

    def move_line_x(self, distance: float):
        for i in self.cords:
            i[0] = i[0] + distance
    
    def move_line_y(self, distance: float):
        for i in self.cords:
            i[1] = i[1] + distance
    
    def move_line_left(self):
        self.move_line_x(-1)

    def move_line_right(self):
        self.move_line_x(1)

    def move_line_up(self):
        self.move_line_y(-1)

    def move_line_down(self):
        self.move_line_x(1)

    def get_initial_pos_x(self):
        return self.initial_cord[0]

    def get_initial_pos_y(self):
        return self.initial_cord[1]

    def get_final_pos_x(self):
        return self.final_cord[0]

    def get_final_pos_y(self):
        return self. final_cord[1]
    
