from typing import List, Tuple


def parse_pontos(texto: str) -> List[Tuple[float, float]]:
    valor = eval(texto, {"__builtins__": {}})

    if isinstance(valor, tuple) and len(valor) == 2 and all(isinstance(c, (int, float)) for c in valor):
        pontos = [valor]
    else:
        pontos = list(valor)

    return [(float(x), float(y)) for x, y in pontos]
