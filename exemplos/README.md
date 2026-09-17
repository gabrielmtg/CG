# Mundos de exemplo (Wavefront .obj)

Use **Carregar .obj** no SGI para abrir qualquer um destes arquivos. Todos cabem
na window inicial (0..1000 em x e y).

| Arquivo | O que testa |
|---|---|
| `mundo_basico.obj` | Os mesmos três objetos iniciais do SGI, com cores no `.mtl`. Bom para conferir o round-trip salvar → carregar. |
| `casa.obj` | Cena com vários wireframes fechados (`f`), retas (`l`), uma polilinha aberta (`chamine`) e um ponto (`macaneta`). Muitos objetos com cores diferentes. |
| `formas.obj` | Polígonos regulares, estrela, "círculo" de 32 lados, espiral e zigue-zague abertos, e um `p` com vários índices (vira `grade`, `grade_2`, ...). Bom para testar escala/rotação em torno do centro e a rotação da window. |
| `blender_cubo.obj` | Formato exatamente como o Blender exporta: cabeçalho, `vt`/`vn`, `s off`, faces `f v/vt/vn`, `.mtl` completo (`Ns`, `Ka`, `Kd`, ...) e círculo exportado como uma aresta `l` por linha. Arquivo 3D: o SGI ignora `z`. |
| `sem_mtl.obj` | Sem `.mtl` (cor padrão), `usemtl` inexistente, índices negativos, `l` fechada repetindo o primeiro índice, grupo `g`, blocos só com vértices e nomes com espaço. |

Para gerar um arquivo novo, basta criar objetos no SGI e usar **Salvar .obj**: o
programa escreve o `.obj` e um `.mtl` de mesmo nome com a cor RGB de cada objeto.
