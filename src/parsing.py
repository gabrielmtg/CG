from typing import List, Optional, Tuple


def _avaliar_tuplas(texto: str, tamanhos: Tuple[int, ...]) -> list:
    valor = eval(texto, {"__builtins__": {}})
    if isinstance(valor, tuple) and len(valor) in tamanhos and all(isinstance(c, (int, float)) for c in valor):
        return [valor]
    return list(valor)


def parse_pontos(texto: str) -> List[Tuple[float, float, float]]:
    pontos = []
    for p in _avaliar_tuplas(texto, (2, 3)):
        if len(p) == 2:
            x, y = p
            z = 0.0
        elif len(p) == 3:
            x, y, z = p
        else:
            raise ValueError("Cada ponto deve ter 2 ou 3 coordenadas.")
        pontos.append((float(x), float(y), float(z)))
    return pontos


def parse_arestas(texto: str, n_vertices: int) -> Optional[List[Tuple[int, int]]]:
    texto = texto.strip()
    if not texto:
        return None
    arestas = []
    for par in _avaliar_tuplas(texto, (2,)):
        if len(par) != 2:
            raise ValueError("Cada aresta deve ser um par (i,j).")
        i, j = int(par[0]), int(par[1])
        if not (1 <= i <= n_vertices and 1 <= j <= n_vertices) or i == j:
            raise ValueError(f"Aresta ({i},{j}) inválida: use índices de 1 a {n_vertices}, distintos.")
        arestas.append((i - 1, j - 1))
    return arestas
