import os
import tkinter as tk
from typing import Dict, Iterable, List, Tuple

from src.ObjGrafic import ObjGrafic
from src.ObjDot import ObjDot
from src.ObjLine import ObjLine
from src.ObjWireframe import ObjWireframe

COR_PADRAO = "#000000"


def cor_para_rgb(cor_hex: str) -> Tuple[float, float, float]:
    """'#RRGGBB' -> (r, g, b) com componentes em [0, 1], como no .mtl."""
    cor_hex = cor_hex.lstrip("#")
    r, g, b = (int(cor_hex[i:i + 2], 16) for i in (0, 2, 4))
    return r / 255, g / 255, b / 255


def rgb_para_cor(r: float, g: float, b: float) -> str:
    """(r, g, b) em [0, 1] -> '#RRGGBB'."""
    def canal(v):
        return max(0, min(255, round(float(v) * 255)))
    return "#{:02X}{:02X}{:02X}".format(canal(r), canal(g), canal(b))


class DescritorOBJ:
    """Transcreve objetos gráficos de/para o formato Wavefront .obj.

    Cada objeto vira um bloco `o <nome>` com seus vértices (`v x y 0`) e um
    elemento com suas arestas: `p` para ponto, `l` para reta/polilinha aberta
    e `f` para wireframe fechado. Os índices de vértice são globais ao
    arquivo (base 1), como manda o formato.

    A cor (RGB) de cada objeto vai em um arquivo .mtl de mesmo nome,
    referenciado por `mtllib`, com um material por objeto (`newmtl`/`Kd`)
    e selecionado no .obj por `usemtl`.
    """

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------
    @staticmethod
    def nome_material(obj: ObjGrafic) -> str:
        return "mat_" + obj.get_name().replace(" ", "_")

    @staticmethod
    def descrever(obj: ObjGrafic, offset: int) -> List[str]:
        """Linhas .obj de um objeto. `offset` é o total de vértices já
        escritos no arquivo antes deste objeto."""
        pontos = obj.get_points()
        linhas = [f"o {obj.get_name()}"]
        for x, y in pontos:
            linhas.append(f"v {x:.6f} {y:.6f} 0.000000")
        linhas.append(f"usemtl {DescritorOBJ.nome_material(obj)}")

        indices = " ".join(str(offset + i) for i in range(1, len(pontos) + 1))
        tipo = obj.get_type()
        if tipo == "ponto":
            linhas.append(f"p {indices}")
        elif tipo == "reta" or not getattr(obj, "closed", True):
            linhas.append(f"l {indices}")
        else:
            linhas.append(f"f {indices}")
        return linhas

    @staticmethod
    def descrever_material(obj: ObjGrafic) -> List[str]:
        r, g, b = cor_para_rgb(obj.get_color())
        return [f"newmtl {DescritorOBJ.nome_material(obj)}",
                f"Kd {r:.6f} {g:.6f} {b:.6f}"]

    @staticmethod
    def salvar(caminho: str, objetos: Iterable[ObjGrafic]):
        objetos = list(objetos)
        caminho_mtl = os.path.splitext(caminho)[0] + ".mtl"

        linhas_obj = ["# Mundo exportado pelo SGI", f"mtllib {os.path.basename(caminho_mtl)}", ""]
        linhas_mtl = ["# Materiais (cores RGB) do SGI", ""]
        offset = 0
        for obj in objetos:
            linhas_obj += DescritorOBJ.descrever(obj, offset) + [""]
            linhas_mtl += DescritorOBJ.descrever_material(obj) + [""]
            offset += len(obj.get_points())

        with open(caminho, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas_obj))
        with open(caminho_mtl, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas_mtl))

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------
    @staticmethod
    def carregar_mtl(caminho: str) -> Dict[str, str]:
        materiais: Dict[str, str] = {}
        if not os.path.exists(caminho):
            return materiais
        atual = None
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                partes = linha.split()
                if not partes or partes[0].startswith("#"):
                    continue
                if partes[0] == "newmtl":
                    atual = linha[len("newmtl"):].strip()
                    materiais[atual] = COR_PADRAO
                elif partes[0] == "Kd" and atual is not None and len(partes) >= 4:
                    materiais[atual] = rgb_para_cor(*partes[1:4])
        return materiais

    @staticmethod
    def carregar(caminho: str, canvas: tk.Canvas) -> List[ObjGrafic]:
        pasta = os.path.dirname(caminho)
        vertices: List[Tuple[float, float]] = []
        materiais: Dict[str, str] = {}
        objetos: List[ObjGrafic] = []
        nomes_usados = set()

        estado = {"nome": None, "cor": COR_PADRAO, "vertices_bloco": [], "tem_elemento": False}

        def nome_unico(base: str) -> str:
            nome, n = base, 1
            while nome in nomes_usados:
                n += 1
                nome = f"{base}_{n}"
            nomes_usados.add(nome)
            return nome

        def indice(token: str) -> int:
            i = int(token.split("/")[0])
            return len(vertices) + i if i < 0 else i - 1

        def criar(pontos, tipo_forcado=None, fechado=True):
            nome = nome_unico(estado["nome"] or "objeto")
            cor = estado["cor"]
            if tipo_forcado == "ponto" or len(pontos) == 1:
                objetos.append(ObjDot(canvas, nome, cor, *pontos[0]))
            elif len(pontos) == 2:
                objetos.append(ObjLine(canvas, nome, cor, *pontos[0], *pontos[1]))
            else:
                objetos.append(ObjWireframe(canvas, nome, cor, pontos, closed=fechado))
            estado["tem_elemento"] = True

        def fechar_bloco():
            # Bloco com vértices mas sem elementos (`p`/`l`/`f`): interpreta
            # os vértices em sequência como um único objeto.
            if not estado["tem_elemento"] and estado["vertices_bloco"]:
                criar([vertices[i] for i in estado["vertices_bloco"]])
            estado["vertices_bloco"] = []
            estado["tem_elemento"] = False

        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                partes = linha.split()
                if not partes or partes[0].startswith("#"):
                    continue
                cmd, args = partes[0], partes[1:]

                if cmd == "mtllib":
                    for nome_mtl in args:
                        materiais.update(DescritorOBJ.carregar_mtl(os.path.join(pasta, nome_mtl)))
                elif cmd == "usemtl":
                    estado["cor"] = materiais.get(linha[len("usemtl"):].strip(), COR_PADRAO)
                elif cmd in ("o", "g"):
                    fechar_bloco()
                    estado["nome"] = linha[1:].strip() or None
                elif cmd == "v":
                    vertices.append((float(args[0]), float(args[1])))
                    estado["vertices_bloco"].append(len(vertices) - 1)
                elif cmd == "p":
                    for token in args:
                        criar([vertices[indice(token)]], tipo_forcado="ponto")
                elif cmd == "l":
                    idx = [indice(t) for t in args]
                    fechado = len(idx) > 2 and idx[0] == idx[-1]
                    if fechado:
                        idx = idx[:-1]
                    criar([vertices[i] for i in idx], fechado=fechado)
                elif cmd == "f":
                    criar([vertices[indice(t)] for t in args], fechado=True)

        fechar_bloco()
        return objetos
