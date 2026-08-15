from abc import ABC, abstractmethod
import tkinter as tk

class ObjGrafic(ABC):
    
    def __init__(self, canvas: tk.Canvas, name: str, color: str):
        self.name = name
        self.color = color
        self.canvas = canvas
        self.id_obj = None

    @abstractmethod
    def draw(self):
        pass
    
    @abstractmethod
    def erase(self):
        pass

    def get_name(self):
        return self.name

    def get_color(self):
        return self.color
