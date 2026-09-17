from typing import List, Optional, Sequence, Tuple

Ponto = Tuple[float, float]
Segmento = Tuple[Ponto, Ponto]

ACIMA = 0b1000
ABAIXO = 0b0100
DIREITA = 0b0010
ESQUERDA = 0b0001


class Clipping:
    COHEN_SUTHERLAND = "Cohen-Sutherland"
    LIANG_BARSKY = "Liang-Barsky"
    ALGORITMOS_RETA = (COHEN_SUTHERLAND, LIANG_BARSKY)

    def __init__(self, algoritmo_reta: str = COHEN_SUTHERLAND,
                 xmin: float = -1.0, ymin: float = -1.0, xmax: float = 1.0, ymax: float = 1.0):
        self.algoritmo_reta = algoritmo_reta
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def ponto(self, p: Ponto) -> Optional[Ponto]:
        x, y = p
        if self.xmin <= x <= self.xmax and self.ymin <= y <= self.ymax:
            return p
        return None

    def reta(self, p1: Ponto, p2: Ponto) -> Optional[Segmento]:
        if self.algoritmo_reta == self.LIANG_BARSKY:
            return self.liang_barsky(p1, p2)
        return self.cohen_sutherland(p1, p2)

    def codigo_regiao(self, x: float, y: float) -> int:
        rc = 0
        if y > self.ymax:
            rc |= ACIMA
        elif y < self.ymin:
            rc |= ABAIXO
        if x > self.xmax:
            rc |= DIREITA
        elif x < self.xmin:
            rc |= ESQUERDA
        return rc

    def cohen_sutherland(self, p1: Ponto, p2: Ponto) -> Optional[Segmento]:
        (x1, y1), (x2, y2) = p1, p2
        rc1 = self.codigo_regiao(x1, y1)
        rc2 = self.codigo_regiao(x2, y2)

        while True:
            if rc1 == 0 and rc2 == 0:
                return (x1, y1), (x2, y2)
            if rc1 & rc2:
                return None

            rc = rc1 if rc1 else rc2
            if rc & ACIMA:
                x = x1 + (x2 - x1) * (self.ymax - y1) / (y2 - y1)
                y = self.ymax
            elif rc & ABAIXO:
                x = x1 + (x2 - x1) * (self.ymin - y1) / (y2 - y1)
                y = self.ymin
            elif rc & DIREITA:
                y = y1 + (y2 - y1) * (self.xmax - x1) / (x2 - x1)
                x = self.xmax
            else:
                y = y1 + (y2 - y1) * (self.xmin - x1) / (x2 - x1)
                x = self.xmin

            if rc == rc1:
                x1, y1 = x, y
                rc1 = self.codigo_regiao(x1, y1)
            else:
                x2, y2 = x, y
                rc2 = self.codigo_regiao(x2, y2)

    def liang_barsky(self, p1: Ponto, p2: Ponto) -> Optional[Segmento]:
        (x1, y1), (x2, y2) = p1, p2
        dx, dy = x2 - x1, y2 - y1
        p = (-dx, dx, -dy, dy)
        q = (x1 - self.xmin, self.xmax - x1, y1 - self.ymin, self.ymax - y1)

        u1, u2 = 0.0, 1.0
        for pk, qk in zip(p, q):
            if pk == 0:
                if qk < 0:
                    return None
                continue
            r = qk / pk
            if pk < 0:
                u1 = max(u1, r)
            else:
                u2 = min(u2, r)

        if u1 > u2:
            return None
        return (x1 + u1 * dx, y1 + u1 * dy), (x1 + u2 * dx, y1 + u2 * dy)

    def poligono(self, pontos: Sequence[Ponto]) -> List[Ponto]:
        bordas = ((0, self.xmin, 1), (0, self.xmax, -1), (1, self.ymin, 1), (1, self.ymax, -1))
        saida = list(pontos)
        for borda in bordas:
            entrada, saida = saida, []
            if not entrada:
                break
            anterior = entrada[-1]
            for atual in entrada:
                if self._dentro(atual, borda):
                    if not self._dentro(anterior, borda):
                        saida.append(self._intersecao(anterior, atual, borda))
                    saida.append(atual)
                elif self._dentro(anterior, borda):
                    saida.append(self._intersecao(anterior, atual, borda))
                anterior = atual
        return self._sem_repetidos(saida)

    @staticmethod
    def _sem_repetidos(pontos: List[Ponto]) -> List[Ponto]:
        resultado = []
        for p in pontos:
            if not resultado or p != resultado[-1]:
                resultado.append(p)
        if len(resultado) > 1 and resultado[0] == resultado[-1]:
            resultado.pop()
        return resultado

    @staticmethod
    def _dentro(p: Ponto, borda) -> bool:
        eixo, valor, sinal = borda
        return (p[eixo] - valor) * sinal >= 0

    @staticmethod
    def _intersecao(p: Ponto, q: Ponto, borda) -> Ponto:
        eixo, valor, _ = borda
        t = (valor - p[eixo]) / (q[eixo] - p[eixo])
        return p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])
