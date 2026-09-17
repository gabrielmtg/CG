# Mundos de exemplo (Wavefront .obj)

Use **Carregar .obj** no SGI para abrir qualquer um destes arquivos.

Convenção dos elementos: `p` ponto, `l` reta ou polilinha aberta,
`l a b c a` (repetindo o primeiro índice) contorno fechado em wireframe,
`f` polígono preenchido. As cores RGB ficam no `.mtl` de mesmo nome.

| Arquivo | O que testa |
|---|---|
| `mundo_basico.obj` | Os mesmos três objetos iniciais do SGI, com cores no `.mtl`. Bom para conferir o round-trip salvar → carregar. |
| `casa.obj` | Cena com polígonos preenchidos (`telhado`, `porta`, `sol`, `arvore_copa`), contornos em wireframe (`parede`, janelas), retas, uma polilinha aberta (`chamine`) e um ponto (`macaneta`). |
| `formas.obj` | Primeira linha de formas preenchida, segunda em wireframe (hexágono, círculo de 32 lados, estrela côncava), espiral e zigue-zague abertos, e um `p` com vários índices (vira `grade`, `grade_2`, ...). Bom para transformações e rotação da window. |
| `clipping.obj` | Objetos que cruzam as bordas da window inicial: retas atravessando uma ou duas bordas, retas totalmente fora, polígonos preenchidos e wireframes parcialmente fora, um círculo maior que a window e pontos dentro/na borda/fora. Nada deve aparecer fora da moldura vermelha. Troque o algoritmo de retas no radio button e navegue/gire a window para ver o recorte acompanhar. |
| `blender_cubo.obj` | Formato exatamente como o Blender exporta: cabeçalho, `vt`/`vn`, `s off`, faces `f v/vt/vn` (viram preenchidas), `.mtl` completo (`Ns`, `Ka`, `Kd`, ...) e círculo exportado como uma aresta `l` por linha. Arquivo 3D: o SGI ignora `z`. |
| `sem_mtl.obj` | Sem `.mtl` (cor padrão), `usemtl` inexistente, índices negativos, `f` preenchido, `l` fechada repetindo o primeiro índice, grupo `g`, blocos só com vértices e nomes com espaço. |

Para gerar um arquivo novo, basta criar objetos no SGI e usar **Salvar .obj**: o
programa escreve o `.obj` e um `.mtl` de mesmo nome com a cor RGB de cada objeto.
