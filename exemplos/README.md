# Mundos de exemplo (Wavefront .obj)

Use **Carregar .obj** no SGI para abrir qualquer um destes arquivos.

Os vértices são 3D (`v x y z`). Um bloco `o` com **várias** arestas (`l`) ou faces (`f`)
é carregado como um `Objeto3D` (modelo de arame); um bloco com um único elemento vira o
objeto 2D correspondente. Gire a window em X/Y para ver a profundidade.

Convenção dos elementos: `p` ponto, `l` reta ou polilinha aberta,
`l a b c a` (repetindo o primeiro índice) contorno fechado em wireframe,
`f` polígono preenchido, `cstype bezier` + `deg 3` + `curv` curva de Bézier cúbica
(4 pontos por segmento, compartilhando o último com o próximo), `cstype bspline` + `deg 3` +
`curv` B-Spline cúbica uniforme (qualquer quantidade de pontos a partir de 4; o vetor de nós em
`parm u` é sempre tratado como uniforme).
As cores RGB ficam no `.mtl` de mesmo nome.

| Arquivo | O que testa |
|---|---|
| `mundo_basico.obj` | Os mesmos três objetos iniciais do SGI, com cores no `.mtl`. Bom para conferir o round-trip salvar → carregar. |
| `casa.obj` | Cena com polígonos preenchidos (`telhado`, `porta`, `sol`, `arvore_copa`), contornos em wireframe (`parede`, janelas), retas, uma polilinha aberta (`chamine`) e um ponto (`macaneta`). |
| `formas.obj` | Primeira linha de formas preenchida, segunda em wireframe (hexágono, círculo de 32 lados, estrela côncava), espiral e zigue-zague abertos, e um `p` com vários índices (vira `grade`, `grade_2`, ...). Bom para transformações e rotação da window. |
| `clipping.obj` | Objetos que cruzam as bordas da window inicial: retas atravessando uma ou duas bordas, retas totalmente fora, polígonos preenchidos e wireframes parcialmente fora, um círculo maior que a window e pontos dentro/na borda/fora. Nada deve aparecer fora da moldura vermelha. Troque o algoritmo de retas no radio button e navegue/gire a window para ver o recorte acompanhar. |
| `curvas.obj` | Curvas de Bézier: um arco simples, uma onda com 3 segmentos e continuidade G(1) (pontos colineares na junção), uma curva com "bico" (só G(0)), um laço e uma curva que sai e volta para a window (testa o clipping da curva). Selecione uma curva e use "Deformar Objeto" para mover os pontos de controle. |
| `bsplines.obj` | B-Splines desenhadas com forward differences: uma curva aberta, a curva com um ponto de controle fora da reta (Figura 4.19), uma curva fechada (3 primeiros pontos repetidos no fim) e uma semifechada (Figura 4.20), uma onda com 16 pontos de controle e uma curva que sai e volta para a window (clipping). |
| `objetos3d.obj` | Modelos de arame 3D: cubo, pirâmide, octaedro e prisma hexagonal (cada um um `Objeto3D`), uma hélice 3D e três eixos de referência saindo do centro da window. De frente parecem figuras 2D; gire a window para ver os volumes. |
| `blender_cubo.obj` | Formato exatamente como o Blender exporta: cabeçalho, `vt`/`vn`, `s off`, faces `f v/vt/vn`, `.mtl` completo (`Ns`, `Ka`, `Kd`, ...) e círculo exportado como uma aresta `l` por linha. O `Cube` (6 faces) e o `Circle` (12 arestas) viram `Objeto3D`; o `Plane` (uma face) vira um polígono preenchido. |
| `sem_mtl.obj` | Sem `.mtl` (cor padrão), `usemtl` inexistente, índices negativos, `f` preenchido, `l` fechada repetindo o primeiro índice, grupo `g`, blocos só com vértices e nomes com espaço. |

Para gerar um arquivo novo, basta criar objetos no SGI e usar **Salvar .obj**: o
programa escreve o `.obj` e um `.mtl` de mesmo nome com a cor RGB de cada objeto.
