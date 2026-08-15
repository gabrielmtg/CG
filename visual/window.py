import tkinter as tk
from tkinter import Tk, ttk

from src.ObjGrafic import ObjGrafic
from src.ObjDot import ObjDot
from src.ObjLine import ObjLine


def functions_menu(root: Tk, objects: dict, canva: tk.Canvas):
    main_section = ttk.Frame(root, padding=20)
    main_section.pack(side="left")
    ttk.Label(main_section, text="Menu de Funções").pack(side="top")
    
    camera_section = ttk.Frame(main_section, padding=10)
    camera_section.pack(side="top", pady=20)
    ttk.Label(camera_section, text="Controle da Câmera (Tela)").grid(row=0, column=0, columnspan=3, pady=5)

    def zoom_in():
        canva.scale("all", 600, 600, 1.2, 1.2) 

    def zoom_out():
        canva.scale("all", 600, 600, 0.8, 0.8)

    def pan_up():
        canva.move("all", 0, 20)

    def pan_down():
        canva.move("all", 0, -20)

    def pan_left():
        canva.move("all", 20, 0)

    def pan_right():
        canva.move("all", -20, 0)

    ttk.Button(camera_section, text="Zoom In (+)", command=zoom_in).grid(row=1, column=0, padx=2, pady=5)
    ttk.Button(camera_section, text="Zoom Out (-)", command=zoom_out).grid(row=1, column=2, padx=2, pady=5)
    
    ttk.Button(camera_section, text="Subir", command=pan_up).grid(row=2, column=1)
    ttk.Button(camera_section, text="Descer", command=pan_down).grid(row=4, column=1)
    ttk.Button(camera_section, text="Ir Esq.", command=pan_left).grid(row=3, column=0)
    ttk.Button(camera_section, text="Ir Dir.", command=pan_right).grid(row=3, column=2)

    seletor_section = ttk.Frame(main_section, padding=10)
    seletor_section.pack(side="top", fill="x")
    ttk.Label(seletor_section, text="Selecionar Objeto (Tag):").pack(side="top")
    
    combo_objetos = ttk.Combobox(seletor_section, state="readonly")
    combo_objetos.pack(side="top", pady=5)

    actions_section = ttk.Frame(main_section, padding=30)
    actions_section.pack(side="top")
    ttk.Label(actions_section, text="ações de movimento").grid(row=0, column=1)

    distancia = 5
    
    def mover(direcao):
        tag_selecionada = combo_objetos.get()
        
        if tag_selecionada in objects:
            obj = objects[tag_selecionada]
            
            if direcao == "cima":
                obj.move_up(distancia)
            elif direcao == "baixo":
                obj.move_down(distancia)
            elif direcao == "esquerda":
                obj.move_left(distancia)
            elif direcao == "direita":
                obj.move_right(distancia)

    ttk.Button(actions_section, text="cima", command=lambda: mover("cima")).grid(row=1, column=1)
    ttk.Button(actions_section, text="baixo", command=lambda: mover("baixo")).grid(row=3, column=1)
    ttk.Button(actions_section, text="esquerda", command=lambda: mover("esquerda")).grid(row=2, column=0)
    ttk.Button(actions_section, text="direita", command=lambda: mover("direita")).grid(row=2, column=2)
    
    pontos_section = ttk.Frame(main_section, padding=10)
    
    ttk.Label(pontos_section, text="Deformar Linha (Pontos)").grid(row=0, column=0, columnspan=3, pady=5)

    combo_pontos = ttk.Combobox(pontos_section, state="readonly", values=["Ponto 0", "Ponto 1"])
    combo_pontos.grid(row=1, column=0, columnspan=3, pady=5)
    combo_pontos.current(0) 

    def manipular_ponto(eixo, dist):
        tag_selecionada = combo_objetos.get()
        indice_ponto = combo_pontos.current() 
        if tag_selecionada in objects:
            obj = objects[tag_selecionada]
            if hasattr(obj, 'move_point'):
                if indice_ponto in [0, 1]:
                    obj.move_point(indice_ponto, dist, eixo)

    ttk.Button(pontos_section, text="Cima", command=lambda: manipular_ponto("y", -distancia)).grid(row=2, column=1)
    ttk.Button(pontos_section, text="Baixo", command=lambda: manipular_ponto("y", distancia)).grid(row=4, column=1)
    ttk.Button(pontos_section, text="Esq.", command=lambda: manipular_ponto("x", -distancia)).grid(row=3, column=0)
    ttk.Button(pontos_section, text="Dir.", command=lambda: manipular_ponto("x", distancia)).grid(row=3, column=2)

    def atualizar_visibilidade(event=None):
        tag = combo_objetos.get()
        if tag in objects:
            obj = objects[tag]
            if hasattr(obj, 'move_point'):
                pontos_section.pack(side="top")
            else:
                pontos_section.pack_forget()

    combo_objetos.bind("<<ComboboxSelected>>", atualizar_visibilidade)
    return combo_objetos

def draw_section(canva: tk.Canvas, objects: dict, combo: ttk.Combobox):

    linha0 = ObjLine(canva, "linha0", "red", 100, 100, 500, 500)
    ponto0 = ObjDot(canva, "ponto0", "black", 550, 550)

    linha0.draw()
    ponto0.draw()

    objects[linha0.get_name()] = linha0
    objects[ponto0.get_name()] = ponto0
    
    tags_disponiveis = list(objects.keys())
    combo['values'] = tags_disponiveis
    
    if tags_disponiveis:
        combo.current(0)
        combo.after(100, lambda: combo.event_generate("<<ComboboxSelected>>"))

def main():
    root = tk.Tk()
    root.title("trabalho de CG")
    root.geometry("2400x1600")
    
    objects = dict()
    
    canva = tk.Canvas(root, height=1200, width=1200, bg="blue")
    canva.place(relx=1.0, rely=.50, anchor="e")
    
    combo = functions_menu(root, objects, canva)
    
    draw_section(canva, objects, combo)
    root.mainloop()
