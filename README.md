# APS — Entrega de pacote em grid 

A ideia é fazer uma pessoa buscar um pacote e entregar no destino, desviando dos obstáculos e considerando os pedágios pelo caminho.

Usei como base o que fiz na prova e fui ajustando o que faltava pra funcionar. Mantive a estrutura dos exemplos de blocos e aspirador, com a classe `ProblemaEntrega(State)` e os métodos `successors`, `is_goal`, `cost`, `env` e `h`.

O código está todo no `entrega.py` e roda pelo terminal.

## Como rodar

Primeiro, instale a biblioteca usada no projeto:

```bash
python -m pip install aigyminsper==0.3.9
```

Depois, na pasta onde salvou o arquivo:

```bash
python entrega.py
```

O programa vai perguntar:

```text
Qual o tamanho do grid?
```

É só colocar um inteiro positivo. Por exemplo, `4` gera um mapa 4 × 4 e `10` gera um mapa 10 × 10. Se digitar algo inválido, ele pergunta de novo.


## Como o cenário é montado

Depois de receber o tamanho, o programa sorteia a posição da pessoa, do pacote e do destino. Também sorteia a quantidade e as posições dos obstáculos e dos pedágios.

Os obstáculos não ficam em cima da pessoa, do pacote ou do destino. Já os pedágios podem aparecer nessas posições, porque continuam sendo células por onde dá pra passar.

Pode sair um mapa sem solução mesmo. Nesse caso, o programa avisa em vez de ficar sorteando outro até dar certo.

As coordenadas aparecem como `(linha, coluna)`, começando no zero. Se o tamanho escolhido for `1`, tudo fica na única célula e o pacote já está no destino, com custo zero.

## O que fica guardado no estado

| Variável | O que guarda |
|---|---|
| `mapa` | O terreno: `0` é livre, `-1` é pedágio e `'X'` é obstáculo. |
| `pos_pessoa` | A posição atual da pessoa. |
| `pos_pacote` | A posição atual do pacote. |
| `final` | O destino da entrega. |
| `encomenda` | Se a pessoa está carregando o pacote. |
| `valor_op` | O custo da ação que gerou aquele estado. |

Na prova eu tinha misturado a pessoa com a matriz e marcado por onde ela passava. Aqui deixei as posições separadas do terreno. Assim, a pessoa pode andar sem apagar um pedágio do mapa, por exemplo.

O `env()` usa as posições da pessoa e do pacote e a variável `encomenda` pra identificar o estado. Não precisa guardar o caminho inteiro pra saber quais ações ela pode fazer dali.

## O que ajustei da prova

No `successors`, cada ação agora cria um objeto `ProblemaEntrega`, em vez de devolver só as coordenadas. Os limites também dependem do tamanho escolhido, sem ficar presos ao mapa 4 × 4.

A pessoa pode ir pra cima, baixo, esquerda e direita, respeitando as bordas e os obstáculos. Movimentos bloqueados ficam de fora da busca porque não mudariam o estado e ainda gastariam uma ação.

Também separei as ações de pegar e entregar. Chegar na caixa não pega o pacote automaticamente. Enquanto a pessoa carrega, ele acompanha os movimentos dela; quando ela larga, fica naquela célula.

No `is_goal`, corrigi a ideia de terminar só por chegar ao destino com a mochila: o pacote precisa estar no destino **e já ter sido entregue**.

## Custo e heurística

Cada ação custa `1`. Se a pessoa estiver numa célula com pedágio antes de executar a ação, o custo fica `3`. Isso vale pra andar, pegar e entregar.

A heurística usa a distância de Manhattan:

```python
abs(x - destino_x) + abs(y - destino_y)
```

Na prova eu tinha colocado a ideia de que, quanto mais perto, menor a heurística. Aqui faltava transformar isso numa conta:

- Sem o pacote: distância até o pacote + distância do pacote até o destino + `2`, pra pegar e entregar.
- Com o pacote: distância até o destino + `1`, pra entregar.
- Pacote já entregue: `0`.

Ela ignora obstáculos e pedágios pra não estimar um custo maior do que o mínimo real. Por isso, é admissível.

## Como a busca funciona

A classe `BuscaEntrega` também está no mesmo arquivo. Ela herda de `AEstrela` e continua escolhendo pelo valor `f = g + h`.

Esse ajuste guarda o menor custo encontrado pra cada estado. Se aparecer um caminho mais barato até o mesmo lugar, ele pode substituir o anterior. Isso também evita ficar repetindo movimentos de ida e volta quando não existe solução.

No final, o terminal mostra as posições sorteadas e, se encontrar uma solução, a sequência de ações, o custo total e o tempo da busca.

