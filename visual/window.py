import tkinter as tk
from tkinter import Tk, ttk, messagebox

from src.ObjDot import ObjDot
from src.ObjLine import ObjLine
from src.ObjWireframe import ObjWireframe
from src.DisplayFile import DisplayFile
from src.Viewport import Viewport
from src.parsing import parse_pontos

CANVAS_SIZE = 1000
PASSO_MOVIMENTO = 10
FATOR_ZOOM = 1.2

CORES_DISPONIVEIS = ["black", "red", "blue", "green", "orange", "purple"]
TIPOS_DISPONIVEIS = ["Ponto", "Reta", "Wireframe"]

REPEAT_DELAY_MS = 400
REPEAT_INTERVAL_MS = 60


def bind_hold(widget, action, delay=REPEAT_DELAY_MS, interval=REPEAT_INTERVAL_MS):
    job = {"id": None}

    def repeat():
        action()
        job["id"] = widget.after(interval, repeat)

    def stop(event=None):
        if job["id"] is not None:
            widget.after_cancel(job["id"])
            job["id"] = None

    def start(event=None):
        stop()
        action()
        job["id"] = widget.after(delay, repeat)

    widget.bind("<ButtonPress-1>", start)
    widget.bind("<ButtonRelease-1>", stop)


def novo_objeto_dialog(root: Tk, display_file: DisplayFile, combo_objetos: ttk.Combobox):
    janela = tk.Toplevel(root)
    janela.title("Inserir Objeto")
    janela.grab_set()

    ttk.Label(janela, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    nome_entry = ttk.Entry(janela)
    nome_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(janela, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tipo_combo = ttk.Combobox(janela, state="readonly", values=TIPOS_DISPONIVEIS)
    tipo_combo.current(0)
    tipo_combo.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(janela, text="Cor:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    cor_combo = ttk.Combobox(janela, state="readonly", values=CORES_DISPONIVEIS)
    cor_combo.current(0)
    cor_combo.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(janela, text="Coordenadas:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    coords_entry = ttk.Entry(janela, width=30)
    coords_entry.insert(0, "(x1,y1),(x2,y2),...")
    coords_entry.grid(row=3, column=1, padx=5, pady=5)

    def confirmar():
        nome = nome_entry.get().strip()
        tipo = tipo_combo.get()
        cor = cor_combo.get()
        texto_coords = coords_entry.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Informe um nome para o objeto.")
            return

        if nome in display_file.objects:
            messagebox.showerror("Erro", f"Já existe um objeto chamado '{nome}'.")
            return

        try:
            pontos = parse_pontos(texto_coords)
        except Exception:
            messagebox.showerror("Erro", "Coordenadas inválidas. Use o formato (x1,y1),(x2,y2),...")
            return

        try:
            if tipo == "Ponto":
                if len(pontos) != 1:
                    raise ValueError("Ponto requer exatamente 1 coordenada.")
                obj = ObjDot(display_file.canvas, nome, cor, *pontos[0])
            elif tipo == "Reta":
                if len(pontos) != 2:
                    raise ValueError("Reta requer exatamente 2 coordenadas.")
                obj = ObjLine(display_file.canvas, nome, cor, *pontos[0], *pontos[1])
            else:
                if len(pontos) < 2:
                    raise ValueError("Wireframe requer ao menos 2 coordenadas.")
                obj = ObjWireframe(display_file.canvas, nome, cor, pontos)
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return

        display_file.add(obj)
        combo_objetos['values'] = list(display_file.objects.keys())
        combo_objetos.set(nome)
        combo_objetos.event_generate("<<ComboboxSelected>>")
        janela.destroy()

    botoes = ttk.Frame(janela)
    botoes.grid(row=4, column=0, columnspan=2, pady=10)
    ttk.Button(botoes, text="Cancelar", command=janela.destroy).pack(side="left", padx=5)
    ttk.Button(botoes, text="OK", command=confirmar).pack(side="left", padx=5)


def functions_menu(root: Tk, display_file: DisplayFile) -> ttk.Combobox:
    main_section = ttk.Frame(root, padding=20)
    main_section.pack(side="left", fill="y")
    ttk.Label(main_section, text="Menu de Funções").pack(side="top")

    seletor_section = ttk.Frame(main_section, padding=10)
    seletor_section.pack(side="top", fill="x")
    ttk.Label(seletor_section, text="Lista de Objetos:").pack(side="top")

    combo_objetos = ttk.Combobox(seletor_section, state="readonly")
    combo_objetos.pack(side="top", pady=5)

    novo_section = ttk.Frame(main_section, padding=10)
    novo_section.pack(side="top")
    ttk.Button(novo_section, text="Novo Objeto",
               command=lambda: novo_objeto_dialog(root, display_file, combo_objetos)).pack(side="top")

    camera_section = ttk.Frame(main_section, padding=10)
    camera_section.pack(side="top", pady=20)
    ttk.Label(camera_section, text="Controle da Câmera (Window)").grid(row=0, column=0, columnspan=3, pady=5)

    btn_zoom_in = ttk.Button(camera_section, text="Zoom In (+)")
    btn_zoom_in.grid(row=1, column=0, padx=2, pady=5)
    bind_hold(btn_zoom_in, lambda: display_file.zoom(FATOR_ZOOM))

    btn_zoom_out = ttk.Button(camera_section, text="Zoom Out (-)")
    btn_zoom_out.grid(row=1, column=2, padx=2, pady=5)
    bind_hold(btn_zoom_out, lambda: display_file.zoom(1 / FATOR_ZOOM))

    btn_subir = ttk.Button(camera_section, text="Subir")
    btn_subir.grid(row=2, column=1)
    bind_hold(btn_subir, lambda: display_file.pan(0, PASSO_MOVIMENTO))

    btn_descer = ttk.Button(camera_section, text="Descer")
    btn_descer.grid(row=4, column=1)
    bind_hold(btn_descer, lambda: display_file.pan(0, -PASSO_MOVIMENTO))

    btn_cam_esq = ttk.Button(camera_section, text="Ir Esq.")
    btn_cam_esq.grid(row=3, column=0)
    bind_hold(btn_cam_esq, lambda: display_file.pan(-PASSO_MOVIMENTO, 0))

    btn_cam_dir = ttk.Button(camera_section, text="Ir Dir.")
    btn_cam_dir.grid(row=3, column=2)
    bind_hold(btn_cam_dir, lambda: display_file.pan(PASSO_MOVIMENTO, 0))

    actions_section = ttk.Frame(main_section, padding=30)
    actions_section.pack(side="top")
    ttk.Label(actions_section, text="Mover Objeto").grid(row=0, column=1)

    def mover(dx, dy):
        nome = combo_objetos.get()
        if nome:
            display_file.move_object(nome, dx, dy)

    btn_cima = ttk.Button(actions_section, text="cima")
    btn_cima.grid(row=1, column=1)
    bind_hold(btn_cima, lambda: mover(0, PASSO_MOVIMENTO))

    btn_baixo = ttk.Button(actions_section, text="baixo")
    btn_baixo.grid(row=3, column=1)
    bind_hold(btn_baixo, lambda: mover(0, -PASSO_MOVIMENTO))

    btn_esquerda = ttk.Button(actions_section, text="esquerda")
    btn_esquerda.grid(row=2, column=0)
    bind_hold(btn_esquerda, lambda: mover(-PASSO_MOVIMENTO, 0))

    btn_direita = ttk.Button(actions_section, text="direita")
    btn_direita.grid(row=2, column=2)
    bind_hold(btn_direita, lambda: mover(PASSO_MOVIMENTO, 0))

    pontos_section = ttk.Frame(main_section, padding=10)
    ttk.Label(pontos_section, text="Deformar Objeto (Pontos)").grid(row=0, column=0, columnspan=3, pady=5)

    combo_pontos = ttk.Combobox(pontos_section, state="readonly")
    combo_pontos.grid(row=1, column=0, columnspan=3, pady=5)

    def manipular_ponto(dx, dy):
        nome = combo_objetos.get()
        indice = combo_pontos.current()
        if nome and indice >= 0:
            display_file.move_point(nome, indice, dx, dy)

    btn_pt_cima = ttk.Button(pontos_section, text="Cima")
    btn_pt_cima.grid(row=2, column=1)
    bind_hold(btn_pt_cima, lambda: manipular_ponto(0, PASSO_MOVIMENTO))

    btn_pt_baixo = ttk.Button(pontos_section, text="Baixo")
    btn_pt_baixo.grid(row=4, column=1)
    bind_hold(btn_pt_baixo, lambda: manipular_ponto(0, -PASSO_MOVIMENTO))

    btn_pt_esq = ttk.Button(pontos_section, text="Esq.")
    btn_pt_esq.grid(row=3, column=0)
    bind_hold(btn_pt_esq, lambda: manipular_ponto(-PASSO_MOVIMENTO, 0))

    btn_pt_dir = ttk.Button(pontos_section, text="Dir.")
    btn_pt_dir.grid(row=3, column=2)
    bind_hold(btn_pt_dir, lambda: manipular_ponto(PASSO_MOVIMENTO, 0))

    def atualizar_visibilidade(event=None):
        nome = combo_objetos.get()
        obj = display_file.objects.get(nome)
        if obj is not None and hasattr(obj, "move_point"):
            n_pontos = len(obj.get_points())
            combo_pontos['values'] = [f"Ponto {i}" for i in range(n_pontos)]
            combo_pontos.current(0)
            pontos_section.pack(side="top")
        else:
            pontos_section.pack_forget()

    combo_objetos.bind("<<ComboboxSelected>>", atualizar_visibilidade)
    return combo_objetos


def objetos_iniciais(display_file: DisplayFile, combo: ttk.Combobox):
    display_file.add(ObjLine(display_file.canvas, "linha0", "red", 100, 100, 500, 500))
    display_file.add(ObjDot(display_file.canvas, "ponto0", "black", 550, 550))
    display_file.add(ObjWireframe(display_file.canvas, "triangulo0", "blue",
                                   [(700, 200), (900, 200), (800, 400)]))

    tags_disponiveis = list(display_file.objects.keys())
    combo['values'] = tags_disponiveis
    if tags_disponiveis:
        combo.current(0)
        combo.event_generate("<<ComboboxSelected>>")


def main():
    root = tk.Tk()
    root.title("Trabalho de CG - Entrega 1")

    canva = tk.Canvas(root, height=CANVAS_SIZE, width=CANVAS_SIZE, bg="white")
    canva.pack(side="right", padx=10, pady=10)

    viewport = Viewport(0, 0, CANVAS_SIZE, CANVAS_SIZE, 0, 0, CANVAS_SIZE, CANVAS_SIZE)
    display_file = DisplayFile(canva, viewport)

    combo = functions_menu(root, display_file)
    objetos_iniciais(display_file, combo)

    root.mainloop()
