import os
import tkinter as tk
from typing import Dict, Iterable, List, Tuple

from src.ObjGrafic import ObjGrafic
from src.ObjDot import ObjDot
from src.ObjLine import ObjLine
from src.ObjWireframe import ObjWireframe
from src.ObjCurva import ObjCurva
from src.ObjBSpline import ObjBSpline
from src.Objeto3D import Objeto3D

COR_PADRAO = "#000000"


def cor_para_rgb(cor_hex: str) -> Tuple[float, float, float]:
    cor_hex = cor_hex.lstrip("#")
    r, g, b = (int(cor_hex[i:i + 2], 16) for i in (0, 2, 4))
    return r / 255, g / 255, b / 255


def rgb_para_cor(r: float, g: float, b: float) -> str:
    def canal(v):
        return max(0, min(255, round(float(v) * 255)))
    return "#{:02X}{:02X}{:02X}".format(canal(r), canal(g), canal(b))


class DescritorOBJ:

    @staticmethod
    def nome_material(obj: ObjGrafic) -> str:
        return "mat_" + obj.get_name().replace(" ", "_")

    @staticmethod
    def descrever(obj: ObjGrafic, offset: int) -> List[str]:
        pontos = obj.get_points()
        linhas = [f"o {obj.get_name()}"]
        for x, y, z in pontos:
            linhas.append(f"v {x:.6f} {y:.6f} {z:.6f}")
        linhas.append(f"usemtl {DescritorOBJ.nome_material(obj)}")

        indices = [str(offset + i) for i in range(1, len(pontos) + 1)]
        tipo = obj.get_type()
        if tipo == "ponto":
            linhas.append("p " + " ".join(indices))
        elif tipo == "reta":
            linhas.append("l " + " ".join(indices))
        elif tipo == "objeto3d":
            for i, j in obj.get_arestas():
                linhas.append(f"l {indices[i]} {indices[j]}")
        elif tipo == "curva":
            n_segmentos = (len(pontos) - 1) // 3
            linhas.append("cstype bezier")
            linhas.append("deg 3")
            linhas.append(f"curv 0.000000 {n_segmentos:.6f} " + " ".join(indices))
            linhas.append("parm u " + " ".join(f"{i:.6f}" for i in range(n_segmentos + 1)))
            linhas.append("end")
        elif tipo == "bspline":
            n = len(pontos)
            linhas.append("cstype bspline")
            linhas.append("deg 3")
            linhas.append(f"curv {3:.6f} {n:.6f} " + " ".join(indices))
            linhas.append("parm u " + " ".join(f"{i:.6f}" for i in range(n + 4)))
            linhas.append("end")
        elif getattr(obj, "filled", False):
            linhas.append("f " + " ".join(indices))
        elif getattr(obj, "closed", True):
            linhas.append("l " + " ".join(indices + indices[:1]))
        else:
            linhas.append("l " + " ".join(indices))
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
        vertices: List[Tuple[float, float, float]] = []
        materiais: Dict[str, str] = {}
        objetos: List[ObjGrafic] = []
        nomes_usados = set()

        estado = {"cor": COR_PADRAO, "cstype": "bezier"}
        bloco = {"nome": None, "vertices": [], "elementos": []}

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

        def criar(tipo: str, idx: List[int], cor: str):
            pontos = [vertices[i] for i in idx]
            nome = nome_unico(bloco["nome"] or "objeto")
            fechado = tipo in ("f", "implicito")
            if tipo == "l" and len(idx) > 2 and idx[0] == idx[-1]:
                pontos, fechado = pontos[:-1], True
            if tipo == "bspline" and ObjBSpline.quantidade_valida(len(pontos)):
                objetos.append(ObjBSpline(canvas, nome, cor, pontos))
            elif tipo == "bezier" and ObjCurva.quantidade_valida(len(pontos)):
                objetos.append(ObjCurva(canvas, nome, cor, pontos))
            elif len(pontos) == 1:
                objetos.append(ObjDot(canvas, nome, cor, *pontos[0]))
            elif len(pontos) == 2:
                objetos.append(ObjLine(canvas, nome, cor, pontos[0], pontos[1]))
            else:
                objetos.append(ObjWireframe(canvas, nome, cor, pontos, closed=fechado, filled=tipo == "f"))

        def criar_malha(elementos, cor: str):
            usados: List[int] = []
            arestas = []
            vistas = set()
            for tipo, idx, _ in elementos:
                pares = list(zip(idx, idx[1:]))
                if tipo == "f":
                    pares.append((idx[-1], idx[0]))
                for a, b in pares:
                    if a == b or (min(a, b), max(a, b)) in vistas:
                        continue
                    vistas.add((min(a, b), max(a, b)))
                    for v in (a, b):
                        if v not in usados:
                            usados.append(v)
                    arestas.append((usados.index(a), usados.index(b)))
            objetos.append(Objeto3D(canvas, nome_unico(bloco["nome"] or "objeto"), cor,
                                    [vertices[i] for i in usados], arestas))

        def fechar_bloco():
            elementos = bloco["elementos"]
            if not elementos and bloco["vertices"]:
                criar("implicito", bloco["vertices"], estado["cor"])
            arestas = [e for e in elementos if e[0] in ("l", "f")]
            malha_criada = False
            for tipo, idx, cor in elementos:
                if tipo in ("l", "f") and len(arestas) > 1:
                    if not malha_criada:
                        criar_malha(arestas, cor)
                        malha_criada = True
                elif tipo == "p":
                    for i in idx:
                        criar("p", [i], cor)
                else:
                    criar(tipo, idx, cor)
            bloco["vertices"], bloco["elementos"] = [], []

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
                    bloco["nome"] = linha[1:].strip() or None
                elif cmd == "v":
                    z = float(args[2]) if len(args) > 2 else 0.0
                    vertices.append((float(args[0]), float(args[1]), z))
                    bloco["vertices"].append(len(vertices) - 1)
                elif cmd in ("p", "l", "f"):
                    bloco["elementos"].append((cmd, [indice(t) for t in args], estado["cor"]))
                elif cmd == "cstype" and args:
                    estado["cstype"] = args[-1].lower()
                elif cmd == "curv":
                    tipo_curva = "bspline" if estado["cstype"] == "bspline" else "bezier"
                    bloco["elementos"].append((tipo_curva, [indice(t) for t in args[2:]], estado["cor"]))

        fechar_bloco()
        return objetos
