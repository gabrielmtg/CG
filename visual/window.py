import re
import tkinter as tk
from tkinter import Tk, ttk, messagebox, colorchooser, filedialog

from src.ObjDot import ObjDot
from src.ObjLine import ObjLine
from src.ObjWireframe import ObjWireframe
from src.ObjCurva import ObjCurva
from src.DisplayFile import DisplayFile
from src.Viewport import Viewport
from src.Window import Window
from src.Transform import Transform
from src.DescritorOBJ import DescritorOBJ
from src.Clipping import Clipping
from src.parsing import parse_pontos

CANVAS_SIZE = 1000
MARGEM_VIEWPORT = 20
PASSO_MOVIMENTO = 10
FATOR_ZOOM = 1.2
PASSO_ROTACAO = 15

COR_PADRAO = "#000000"
COR_RGB_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
TIPOS_DISPONIVEIS = ["Ponto", "Reta", "Wireframe", "Curva (Bézier)"]

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


def campo_numerico(parent, texto, row, valor="0"):
    ttk.Label(parent, text=texto).grid(row=row, column=0, sticky="w", padx=5, pady=3)
    entry = ttk.Entry(parent, width=10)
    entry.insert(0, valor)
    entry.grid(row=row, column=1, padx=5, pady=3)
    return entry


def ler_float(entry, nome):
    try:
        return float(entry.get().strip())
    except ValueError:
        raise ValueError(f"Valor inválido para '{nome}'.")


def novo_objeto_dialog(root: Tk, display_file: DisplayFile, combo_objetos: ttk.Combobox):
    janela = tk.Toplevel(root)
    janela.title("Inserir Objeto")
    janela.grab_set()

    ttk.Label(janela, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    nome_entry = ttk.Entry(janela)
    nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(janela, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tipo_combo = ttk.Combobox(janela, state="readonly", values=TIPOS_DISPONIVEIS)
    tipo_combo.current(0)
    tipo_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(janela, text="Cor (RGB):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    cor_frame = ttk.Frame(janela)
    cor_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    cor_entry = ttk.Entry(cor_frame, width=10)
    cor_entry.insert(0, COR_PADRAO)
    cor_entry.pack(side="left")

    cor_preview = tk.Label(cor_frame, width=2, bg=COR_PADRAO, relief="sunken")
    cor_preview.pack(side="left", padx=5)

    def atualizar_preview(event=None):
        cor = cor_entry.get().strip()
        if COR_RGB_RE.match(cor):
            cor_preview.config(bg=cor)

    def escolher_cor():
        _, cor_hex = colorchooser.askcolor(color=cor_entry.get().strip() or COR_PADRAO,
                                           parent=janela, title="Escolher cor")
        if cor_hex:
            cor_entry.delete(0, "end")
            cor_entry.insert(0, cor_hex.upper())
            atualizar_preview()

    cor_entry.bind("<KeyRelease>", atualizar_preview)
    ttk.Button(cor_frame, text="Escolher...", command=escolher_cor).pack(side="left")

    ttk.Label(janela, text="Coordenadas:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    coords_entry = ttk.Entry(janela, width=30)
    coords_entry.insert(0, "(x1,y1),(x2,y2),...")
    coords_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    preenchido_var = tk.BooleanVar(value=False)
    preenchido_check = ttk.Checkbutton(janela, text="Polígono preenchido", variable=preenchido_var)
    preenchido_check.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    def atualizar_preenchido(event=None):
        if tipo_combo.get() == "Wireframe":
            preenchido_check.config(state="normal")
        else:
            preenchido_var.set(False)
            preenchido_check.config(state="disabled")

    tipo_combo.bind("<<ComboboxSelected>>", atualizar_preenchido)
    atualizar_preenchido()

    def confirmar():
        nome = nome_entry.get().strip()
        tipo = tipo_combo.get()
        cor = cor_entry.get().strip().upper()
        texto_coords = coords_entry.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Informe um nome para o objeto.")
            return

        if nome in display_file.objects:
            messagebox.showerror("Erro", f"Já existe um objeto chamado '{nome}'.")
            return

        if not COR_RGB_RE.match(cor):
            messagebox.showerror("Erro", "Cor inválida. Use o formato RGB hexadecimal #RRGGBB.")
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
            elif tipo == "Curva (Bézier)":
                if not ObjCurva.quantidade_valida(len(pontos)):
                    raise ValueError("Curva de Bézier requer 4 + 3k pontos (4, 7, 10, ...): "
                                     "cada segmento usa 4 pontos e compartilha o último com o próximo.")
                obj = ObjCurva(display_file.canvas, nome, cor, pontos)
            else:
                preenchido = preenchido_var.get()
                if preenchido and len(pontos) < 3:
                    raise ValueError("Polígono preenchido requer ao menos 3 coordenadas.")
                if len(pontos) < 2:
                    raise ValueError("Wireframe requer ao menos 2 coordenadas.")
                obj = ObjWireframe(display_file.canvas, nome, cor, pontos, filled=preenchido)
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return

        display_file.add(obj)
        combo_objetos['values'] = list(display_file.objects.keys())
        combo_objetos.set(nome)
        combo_objetos.event_generate("<<ComboboxSelected>>")
        janela.destroy()

    botoes = ttk.Frame(janela)
    botoes.grid(row=5, column=0, columnspan=2, pady=10)
    ttk.Button(botoes, text="Cancelar", command=janela.destroy).pack(side="left", padx=5)
    ttk.Button(botoes, text="OK", command=confirmar).pack(side="left", padx=5)


def transformacao_dialog(root: Tk, display_file: DisplayFile, nome: str):
    obj = display_file.objects.get(nome)
    if obj is None:
        messagebox.showwarning("Aviso", "Selecione um objeto para transformar.")
        return

    janela = tk.Toplevel(root)
    janela.title(f"Transformações 2D - {nome}")
    janela.grab_set()

    esquerda = ttk.Frame(janela, padding=10)
    esquerda.grid(row=0, column=0, sticky="n")
    direita = ttk.Frame(janela, padding=10)
    direita.grid(row=0, column=1, sticky="n")

    abas = ttk.Notebook(esquerda)
    abas.pack(side="top")

    aba_translacao = ttk.Frame(abas, padding=10)
    abas.add(aba_translacao, text="Translação")
    ttk.Label(aba_translacao, text="Relativa à orientação da window").grid(row=0, column=0, columnspan=2, pady=(0, 5))
    dx_entry = campo_numerico(aba_translacao, "Dx:", 1)
    dy_entry = campo_numerico(aba_translacao, "Dy:", 2)

    aba_escala = ttk.Frame(abas, padding=10)
    abas.add(aba_escala, text="Escalonamento")
    ttk.Label(aba_escala, text="Em torno do centro do objeto").grid(row=0, column=0, columnspan=2, pady=(0, 5))
    sx_entry = campo_numerico(aba_escala, "Sx:", 1, "1")
    sy_entry = campo_numerico(aba_escala, "Sy:", 2, "1")

    aba_rotacao = ttk.Frame(abas, padding=10)
    abas.add(aba_rotacao, text="Rotação")

    modo_rotacao = tk.StringVar(value="mundo")
    opcoes = ttk.LabelFrame(aba_rotacao, text="Opções", padding=5)
    opcoes.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 5))
    ttk.Radiobutton(opcoes, text="Em torno do centro do mundo", variable=modo_rotacao,
                    value="mundo").pack(anchor="w")
    ttk.Radiobutton(opcoes, text="Em torno do centro do objeto", variable=modo_rotacao,
                    value="objeto").pack(anchor="w")
    ttk.Radiobutton(opcoes, text="Em torno de um ponto qualquer", variable=modo_rotacao,
                    value="ponto").pack(anchor="w")

    angulo_entry = campo_numerico(aba_rotacao, "Ângulo (graus):", 1)
    px_entry = campo_numerico(aba_rotacao, "Ponto X:", 2)
    py_entry = campo_numerico(aba_rotacao, "Ponto Y:", 3)

    def atualizar_campos_ponto(*args):
        estado = "normal" if modo_rotacao.get() == "ponto" else "disabled"
        px_entry.config(state=estado)
        py_entry.config(state=estado)

    modo_rotacao.trace_add("write", atualizar_campos_ponto)
    atualizar_campos_ponto()

    ttk.Label(direita, text="Transformações:").pack(side="top", anchor="w")
    lista = tk.Listbox(direita, width=42, height=12)
    lista.pack(side="top", pady=5)

    pendentes = []

    def adicionar():
        aba = abas.index(abas.select())
        try:
            if aba == 0:
                dx, dy = ler_float(dx_entry, "Dx"), ler_float(dy_entry, "Dy")
                descricao = f"Translação (dx={dx:g}, dy={dy:g})"
                montar = lambda centro: Transform.matriz_translacao(
                    *display_file.window.to_world_vector(dx, dy))
            elif aba == 1:
                sx, sy = ler_float(sx_entry, "Sx"), ler_float(sy_entry, "Sy")
                descricao = f"Escalonamento (sx={sx:g}, sy={sy:g})"
                montar = lambda centro: Transform.matriz_escala_natural(sx, sy, centro)
            else:
                angulo = ler_float(angulo_entry, "Ângulo")
                modo = modo_rotacao.get()
                if modo == "mundo":
                    descricao = f"Rotação {angulo:g}° (centro do mundo)"
                    montar = lambda centro: Transform.matriz_rotacao(angulo)
                elif modo == "objeto":
                    descricao = f"Rotação {angulo:g}° (centro do objeto)"
                    montar = lambda centro: Transform.matriz_rotacao_ponto(angulo, centro)
                else:
                    px, py = ler_float(px_entry, "Ponto X"), ler_float(py_entry, "Ponto Y")
                    descricao = f"Rotação {angulo:g}° (ponto ({px:g}, {py:g}))"
                    montar = lambda centro: Transform.matriz_rotacao_ponto(angulo, (px, py))
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro), parent=janela)
            return

        pendentes.append((descricao, montar))
        lista.insert("end", descricao)

    def remover():
        selecao = lista.curselection()
        if selecao:
            indice = selecao[0]
            lista.delete(indice)
            pendentes.pop(indice)

    def aplicar():
        if pendentes:
            matriz = Transform.identidade()
            centro_original = obj.get_center()
            for _, montar in pendentes:
                centro_atual = Transform.aplicar_ponto(matriz, centro_original)
                matriz = Transform.mult_matrix(matriz, montar(centro_atual))
            display_file.transform_object(nome, matriz)
        janela.destroy()

    ttk.Button(esquerda, text="Adicionar", command=adicionar).pack(side="top", pady=10, fill="x")

    botoes_lista = ttk.Frame(direita)
    botoes_lista.pack(side="top", fill="x")
    ttk.Button(botoes_lista, text="Remover", command=remover).pack(side="left")

    botoes = ttk.Frame(janela)
    botoes.grid(row=1, column=0, columnspan=2, pady=10)
    ttk.Button(botoes, text="Cancelar", command=janela.destroy).pack(side="left", padx=5)
    ttk.Button(botoes, text="OK", command=aplicar).pack(side="left", padx=5)


def atualizar_lista_objetos(display_file: DisplayFile, combo_objetos: ttk.Combobox):
    nomes = list(display_file.objects.keys())
    combo_objetos['values'] = nomes
    if nomes:
        combo_objetos.set(nomes[0])
    else:
        combo_objetos.set("")
    combo_objetos.event_generate("<<ComboboxSelected>>")


def salvar_obj(display_file: DisplayFile):
    caminho = filedialog.asksaveasfilename(
        title="Salvar mundo", defaultextension=".obj",
        filetypes=[("Wavefront OBJ", "*.obj"), ("Todos", "*.*")])
    if not caminho:
        return
    try:
        DescritorOBJ.salvar(caminho, display_file.objects.values())
    except OSError as erro:
        messagebox.showerror("Erro", f"Não foi possível salvar o arquivo:\n{erro}")


def carregar_obj(display_file: DisplayFile, combo_objetos: ttk.Combobox):
    caminho = filedialog.askopenfilename(
        title="Carregar mundo", filetypes=[("Wavefront OBJ", "*.obj"), ("Todos", "*.*")])
    if not caminho:
        return
    try:
        objetos = DescritorOBJ.carregar(caminho, display_file.canvas)
    except (OSError, ValueError, IndexError) as erro:
        messagebox.showerror("Erro", f"Não foi possível ler o arquivo .obj:\n{erro}")
        return

    if display_file.objects:
        substituir = messagebox.askyesno(
            "Carregar mundo",
            "Substituir os objetos atuais?\n(Não = adicionar ao mundo atual)")
        if substituir:
            display_file.clear()

    for obj in objetos:
        base, n = obj.get_name(), 1
        while obj.get_name() in display_file.objects:
            n += 1
            obj.name = f"{base}_{n}"
        display_file.add(obj)

    atualizar_lista_objetos(display_file, combo_objetos)


def bind_context_menu(root: Tk, display_file: DisplayFile, combo_objetos: ttk.Combobox):
    menu = tk.Menu(root, tearoff=0)

    def abrir_menu(event):
        nome = display_file.find_object_at(event.x, event.y)
        if nome is None:
            return
        combo_objetos.set(nome)
        combo_objetos.event_generate("<<ComboboxSelected>>")
        menu.delete(0, "end")
        menu.add_command(label=f"Transformar '{nome}'...",
                         command=lambda: transformacao_dialog(root, display_file, nome))
        menu.tk_popup(event.x_root, event.y_root)

    display_file.canvas.bind("<Button-3>", abrir_menu)


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
               command=lambda: novo_objeto_dialog(root, display_file, combo_objetos)).pack(side="top", pady=2)
    ttk.Button(novo_section, text="Transformar Objeto",
               command=lambda: transformacao_dialog(root, display_file, combo_objetos.get())).pack(side="top", pady=2)

    arquivo_section = ttk.Frame(main_section, padding=10)
    arquivo_section.pack(side="top")
    ttk.Label(arquivo_section, text="Arquivo (Wavefront .obj)").grid(row=0, column=0, columnspan=2, pady=5)
    ttk.Button(arquivo_section, text="Salvar .obj",
               command=lambda: salvar_obj(display_file)).grid(row=1, column=0, padx=2)
    ttk.Button(arquivo_section, text="Carregar .obj",
               command=lambda: carregar_obj(display_file, combo_objetos)).grid(row=1, column=1, padx=2)

    clip_section = ttk.Frame(main_section, padding=10)
    clip_section.pack(side="top")
    ttk.Label(clip_section, text="Clipagem de Retas").pack(side="top")
    algoritmo_reta = tk.StringVar(value=display_file.clipping.algoritmo_reta)
    for algoritmo in Clipping.ALGORITMOS_RETA:
        ttk.Radiobutton(clip_section, text=algoritmo, variable=algoritmo_reta, value=algoritmo,
                        command=lambda: display_file.set_algoritmo_reta(algoritmo_reta.get())).pack(anchor="w")

    camera_section = ttk.Frame(main_section, padding=10)
    camera_section.pack(side="top", pady=5)
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

    ttk.Label(camera_section, text="Rotação da Window").grid(row=5, column=0, columnspan=3, pady=(15, 5))

    ttk.Label(camera_section, text="Ângulo:").grid(row=6, column=0, sticky="e")
    angulo_entry = ttk.Entry(camera_section, width=6)
    angulo_entry.insert(0, str(PASSO_ROTACAO))
    angulo_entry.grid(row=6, column=1)
    angulo_atual = ttk.Label(camera_section, text="atual: 0°")
    angulo_atual.grid(row=6, column=2)

    def rotacionar_window(sentido):
        try:
            graus = float(angulo_entry.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Ângulo de rotação inválido.")
            return
        display_file.rotate_window(sentido * graus)
        angulo_atual.config(text=f"atual: {display_file.window.get_angle():g}°")

    btn_rot_esq = ttk.Button(camera_section, text="↺ Anti-horário")
    btn_rot_esq.grid(row=7, column=0, padx=2, pady=5)
    bind_hold(btn_rot_esq, lambda: rotacionar_window(+1))

    btn_rot_dir = ttk.Button(camera_section, text="↻ Horário")
    btn_rot_dir.grid(row=7, column=2, padx=2, pady=5)
    bind_hold(btn_rot_dir, lambda: rotacionar_window(-1))

    actions_section = ttk.Frame(main_section, padding=10)
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
    display_file.add(ObjLine(display_file.canvas, "linha0", "#FF0000", 100, 100, 500, 500))
    display_file.add(ObjDot(display_file.canvas, "ponto0", "#000000", 550, 550))
    display_file.add(ObjWireframe(display_file.canvas, "triangulo0", "#0000FF",
                                   [(700, 200), (900, 200), (800, 400)]))

    tags_disponiveis = list(display_file.objects.keys())
    combo['values'] = tags_disponiveis
    if tags_disponiveis:
        combo.current(0)
        combo.event_generate("<<ComboboxSelected>>")


def main():
    root = tk.Tk()
    root.title("Trabalho de CG - SGI 2D")

    canva = tk.Canvas(root, height=CANVAS_SIZE, width=CANVAS_SIZE, bg="white")
    canva.pack(side="right", padx=10, pady=10)

    canva.create_rectangle(MARGEM_VIEWPORT, MARGEM_VIEWPORT,
                           CANVAS_SIZE - MARGEM_VIEWPORT, CANVAS_SIZE - MARGEM_VIEWPORT,
                           outline="red", width=2)

    window = Window(CANVAS_SIZE / 2, CANVAS_SIZE / 2, CANVAS_SIZE, CANVAS_SIZE)
    viewport = Viewport(MARGEM_VIEWPORT, MARGEM_VIEWPORT,
                        CANVAS_SIZE - MARGEM_VIEWPORT, CANVAS_SIZE - MARGEM_VIEWPORT)
    display_file = DisplayFile(canva, window, viewport)

    combo = functions_menu(root, display_file)
    bind_context_menu(root, display_file, combo)
    objetos_iniciais(display_file, combo)

    root.mainloop()
