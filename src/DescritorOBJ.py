import math
import os
import tkinter as tk
from itertools import takewhile
from typing import Dict, Iterable, Iterator, List, Tuple

from src.ObjGrafic import ObjGrafic
from src.ObjDot import ObjDot
from src.ObjLine import ObjLine
from src.ObjWireframe import ObjWireframe
from src.ObjCurva import ObjCurva
from src.ObjBSpline import ObjBSpline
from src.Objeto3D import Objeto3D
from src.ObjSuperficieBezier import ObjSuperficieBezier
from src.ObjSuperficieBSpline import ObjSuperficieBSpline

COR_PADRAO = "#000000"
GRAU_SUPERFICIE = 3


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
        elif tipo == "superficie_bspline":
            matriz = obj.get_matriz()
            n_v, n_u = len(matriz), len(matriz[0])
            controle = " ".join(indices[i] for linha in matriz for i in linha)
            linhas.append("cstype bspline")
            linhas.append("deg 3 3")
            linhas.append(f"surf {3:.6f} {n_u:.6f} {3:.6f} {n_v:.6f} {controle}")
            linhas.append("parm u " + " ".join(f"{i:.6f}" for i in range(n_u + GRAU_SUPERFICIE + 1)))
            linhas.append("parm v " + " ".join(f"{i:.6f}" for i in range(n_v + GRAU_SUPERFICIE + 1)))
            linhas.append("end")
        elif tipo == "superficie_bezier":
            linhas.append("cstype bezier")
            linhas.append("deg 3 3")
            for retalho in obj.get_retalhos():
                controle = " ".join(indices[i] for linha in retalho for i in linha)
                linhas.append(f"surf 0.000000 1.000000 0.000000 1.000000 {controle}")
                linhas.append("parm u 0.000000 1.000000")
                linhas.append("parm v 0.000000 1.000000")
                linhas.append("end")
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
    def linhas_logicas(caminho: str) -> Iterator[str]:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            acumulada = ""
            for linha in f:
                linha = linha.rstrip()
                if linha.endswith("\\"):
                    acumulada += linha[:-1] + " "
                else:
                    yield acumulada + linha
                    acumulada = ""
            if acumulada:
                yield acumulada

    @staticmethod
    def carregar_mtl(caminho: str) -> Dict[str, str]:
        materiais: Dict[str, str] = {}
        if not os.path.exists(caminho):
            return materiais
        atual = None
        for linha in DescritorOBJ.linhas_logicas(caminho):
            partes = linha.split()
            if not partes or partes[0].startswith("#"):
                continue
            if partes[0] == "newmtl":
                atual = linha.split(None, 1)[1].strip() if len(partes) > 1 else ""
                materiais[atual] = COR_PADRAO
            elif partes[0] == "Kd" and atual is not None and len(partes) >= 4:
                materiais[atual] = rgb_para_cor(*partes[1:4])
        return materiais

    @staticmethod
    def carregar(caminho: str, canvas: tk.Canvas) -> List[ObjGrafic]:
        return LeitorOBJ(caminho, canvas).ler()


class LeitorOBJ:

    def __init__(self, caminho: str, canvas: tk.Canvas):
        self.caminho = caminho
        self.pasta = os.path.dirname(caminho)
        self.nome_padrao = os.path.splitext(os.path.basename(caminho))[0]
        self.canvas = canvas
        self.vertices: List[Tuple[float, float, float]] = []
        self.materiais: Dict[str, str] = {}
        self.cor = COR_PADRAO
        self.cstype = "bezier"
        self.deg = ["3"]
        self.blocos = [self.novo_bloco(None, False)]
        self.superficie_aberta = None
        self.objetos: List[ObjGrafic] = []
        self.nomes_usados = set()

    def novo_bloco(self, nome, grupo: bool) -> dict:
        return {"nome": nome, "grupo": grupo, "vertices": [], "elementos": [], "cor": self.cor}

    def ler(self) -> List[ObjGrafic]:
        for linha in DescritorOBJ.linhas_logicas(self.caminho):
            self.processar_linha(linha)
        self.mesclar_grupos()
        referenciados = {i for bloco in self.blocos for e in bloco["elementos"] for i in e["indices"]}
        for bloco in self.blocos:
            self.construir_bloco(bloco, referenciados)
        return self.objetos

    def indice(self, token: str) -> int:
        i = int(token.split("/")[0])
        return len(self.vertices) + i if i < 0 else i - 1

    def adicionar_elemento(self, tipo: str, indices: List[int]) -> dict:
        elemento = {"tipo": tipo, "indices": indices, "cor": self.cor, "parm": {}}
        self.blocos[-1]["elementos"].append(elemento)
        return elemento

    def carregar_mtllib(self, texto: str, nomes: List[str]):
        for nome in ([texto] if os.path.exists(os.path.join(self.pasta, texto)) else nomes):
            self.materiais.update(DescritorOBJ.carregar_mtl(os.path.join(self.pasta, nome)))

    @staticmethod
    def ler_vertice(args: List[str]) -> Tuple[float, float, float]:
        x, y = float(args[0]), float(args[1])
        z = float(args[2]) if len(args) > 2 else 0.0
        if len(args) == 4 and float(args[3]) != 0:
            w = float(args[3])
            return x / w, y / w, z / w
        return x, y, z

    def processar_linha(self, linha: str):
        partes = linha.split()
        if not partes or partes[0].startswith("#"):
            return
        cmd = partes[0]
        args = list(takewhile(lambda t: not t.startswith("#"), partes[1:]))
        texto = linha.split(None, 1)[1].strip() if len(partes) > 1 else ""

        if cmd == "mtllib":
            self.carregar_mtllib(texto, args)
        elif cmd == "usemtl":
            self.cor = self.materiais.get(texto, COR_PADRAO)
            self.blocos[-1]["cor"] = self.cor
        elif cmd in ("o", "g"):
            self.blocos.append(self.novo_bloco(texto or None, cmd == "g"))
        elif cmd == "v":
            self.vertices.append(self.ler_vertice(args))
            self.blocos[-1]["vertices"].append(len(self.vertices) - 1)
        elif cmd in ("p", "l", "f"):
            self.adicionar_elemento(cmd, [self.indice(t) for t in args])
        elif cmd == "cstype" and args:
            self.cstype = args[-1].lower()
        elif cmd == "deg" and args:
            self.deg = args
        elif cmd == "curv":
            tipo = "bspline" if self.cstype == "bspline" else "bezier"
            self.adicionar_elemento(tipo, [self.indice(t) for t in args[2:]])
        elif cmd == "surf":
            self.abrir_superficie([self.indice(t) for t in args[4:]])
        elif cmd == "parm" and self.superficie_aberta is not None and len(args) > 1:
            self.superficie_aberta["parm"][args[0]] = args[1:]
        elif cmd == "end":
            self.superficie_aberta = None

    def abrir_superficie(self, controle: List[int]):
        self.superficie_aberta = None
        if self.deg != ["3", "3"]:
            return
        if self.cstype == "bspline":
            self.superficie_aberta = self.adicionar_elemento("surf_bspline", controle)
        elif self.cstype == "bezier" and len(controle) == 16:
            self.superficie_aberta = self.adicionar_elemento("surf_bezier", controle)

    @staticmethod
    def so_faces(bloco: dict) -> bool:
        return bool(bloco["elementos"]) and all(e["tipo"] in ("l", "f") for e in bloco["elementos"])

    def mesclar_grupos(self):
        pai: Dict[int, int] = {}

        def raiz(i: int) -> int:
            while pai[i] != i:
                pai[i] = pai[pai[i]]
                i = pai[i]
            return i

        dono_do_vertice: Dict[int, int] = {}
        for i, bloco in enumerate(self.blocos):
            if not (bloco["grupo"] and self.so_faces(bloco)):
                continue
            pai[i] = i
            for elemento in bloco["elementos"]:
                for v in elemento["indices"]:
                    a, b = raiz(i), raiz(dono_do_vertice.setdefault(v, i))
                    pai[max(a, b)] = min(a, b)

        mesclados = []
        for i, bloco in enumerate(self.blocos):
            if i in pai and raiz(i) != i:
                principal = self.blocos[raiz(i)]
                principal["elementos"].extend(bloco["elementos"])
                principal["nome"] = None
            else:
                mesclados.append(bloco)
        self.blocos = mesclados

    def nome_unico(self, bloco: dict) -> str:
        base = bloco["nome"] or self.nome_padrao
        nome, n = base, 1
        while nome in self.nomes_usados:
            n += 1
            nome = f"{base}_{n}"
        self.nomes_usados.add(nome)
        return nome

    def criar(self, bloco: dict, tipo: str, idx: List[int], cor: str):
        pontos = [self.vertices[i] for i in idx]
        nome = self.nome_unico(bloco)
        fechado = tipo in ("f", "implicito")
        if tipo == "l" and len(idx) > 2 and idx[0] == idx[-1]:
            pontos, fechado = pontos[:-1], True
        if tipo == "bspline" and ObjBSpline.quantidade_valida(len(pontos)):
            self.objetos.append(ObjBSpline(self.canvas, nome, cor, pontos))
        elif tipo == "bezier" and ObjCurva.quantidade_valida(len(pontos)):
            self.objetos.append(ObjCurva(self.canvas, nome, cor, pontos))
        elif len(pontos) == 1:
            self.objetos.append(ObjDot(self.canvas, nome, cor, *pontos[0]))
        elif len(pontos) == 2:
            self.objetos.append(ObjLine(self.canvas, nome, cor, pontos[0], pontos[1]))
        else:
            self.objetos.append(ObjWireframe(self.canvas, nome, cor, pontos, closed=fechado, filled=tipo == "f"))

    def criar_malha(self, bloco: dict, elementos: List[dict], cor: str):
        usados: Dict[int, int] = {}
        arestas = []
        vistas = set()
        for elemento in elementos:
            idx = elemento["indices"]
            pares = list(zip(idx, idx[1:]))
            if elemento["tipo"] == "f":
                pares.append((idx[-1], idx[0]))
            for a, b in pares:
                if a == b or (min(a, b), max(a, b)) in vistas:
                    continue
                vistas.add((min(a, b), max(a, b)))
                usados.setdefault(a, len(usados))
                usados.setdefault(b, len(usados))
                arestas.append((usados[a], usados[b]))
        self.objetos.append(Objeto3D(self.canvas, self.nome_unico(bloco), cor,
                                     [self.vertices[i] for i in usados], arestas))

    def criar_superficie_bezier(self, bloco: dict, elementos: List[dict], cor: str):
        usados: Dict[int, int] = {}
        for elemento in elementos:
            for v in elemento["indices"]:
                usados.setdefault(v, len(usados))
        retalhos = [[[usados[e["indices"][4 * i + j]] for j in range(4)] for i in range(4)] for e in elementos]
        self.objetos.append(ObjSuperficieBezier(self.canvas, self.nome_unico(bloco), cor,
                                                [self.vertices[i] for i in usados], retalhos))

    @staticmethod
    def dimensoes_bspline(elemento: dict) -> Tuple[int, int]:
        total = len(elemento["indices"])
        n_u = len(elemento["parm"].get("u", [])) - GRAU_SUPERFICIE - 1
        n_v = len(elemento["parm"].get("v", [])) - GRAU_SUPERFICIE - 1
        if n_u * n_v == total and n_u > 0:
            return n_v, n_u
        lado = math.isqrt(total)
        if lado * lado == total:
            return lado, lado
        raise ValueError(f"Superfície B-Spline com {total} pontos de controle não corresponde aos nós de 'parm u/v'.")

    def criar_superficie_bspline(self, bloco: dict, elemento: dict):
        linhas, colunas = self.dimensoes_bspline(elemento)
        usados: Dict[int, int] = {}
        for v in elemento["indices"]:
            usados.setdefault(v, len(usados))
        matriz = [[usados[elemento["indices"][colunas * i + j]] for j in range(colunas)] for i in range(linhas)]
        self.objetos.append(ObjSuperficieBSpline(self.canvas, self.nome_unico(bloco), elemento["cor"],
                                                 [self.vertices[i] for i in usados], matriz))

    def construir_bloco(self, bloco: dict, referenciados: set):
        elementos = bloco["elementos"]
        if not elementos:
            livres = [i for i in bloco["vertices"] if i not in referenciados]
            if livres:
                self.criar(bloco, "implicito", livres, bloco["cor"])
            return
        arestas = [e for e in elementos if e["tipo"] in ("l", "f")]
        retalhos = [e for e in elementos if e["tipo"] == "surf_bezier"]
        malha_criada = bezier_criada = False
        for elemento in elementos:
            tipo, idx, cor = elemento["tipo"], elemento["indices"], elemento["cor"]
            if tipo == "surf_bezier":
                if not bezier_criada:
                    self.criar_superficie_bezier(bloco, retalhos, cor)
                    bezier_criada = True
            elif tipo == "surf_bspline":
                self.criar_superficie_bspline(bloco, elemento)
            elif tipo in ("l", "f") and len(arestas) > 1:
                if not malha_criada:
                    self.criar_malha(bloco, arestas, cor)
                    malha_criada = True
            elif tipo == "p":
                for i in idx:
                    self.criar(bloco, "p", [i], cor)
            else:
                self.criar(bloco, tipo, idx, cor)
