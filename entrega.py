from aigyminsper.search.search_algorithms import AEstrela
from aigyminsper.search.graph import State, Node
import random
import time


class ProblemaEntrega(State):

    def __init__(self, op, mapa, pos_pessoa, pos_pacote, final, encomenda=False, valor_op=0):
        super().__init__(op)
        self.op = op
        self.mapa = mapa
        self.pos_pessoa = pos_pessoa
        self.pos_pacote = pos_pacote
        self.final = final
        self.encomenda = encomenda
        self.valor_op = valor_op

        # na prova eu misturei a pessoa com o mapa. aqui deixei as posicoes separadas
        # no mapa ficou so o terreno: 0 livre, -1 pedagio e X obstaculo

    def __print__(self):
        resposta = f'\nOperacao: {self.op}'
        resposta += f'\nPessoa: {self.pos_pessoa}'
        resposta += f'\nPacote: {self.pos_pacote}'
        resposta += f'\nCom a encomenda: {self.encomenda}'
        return resposta

    def successors(self):
        successors = []
        x, y = self.pos_pessoa
        n = len(self.mapa)

        # o pedagio conta onde a pessoa esta antes de fazer a acao
        valor_op = 1
        if self.mapa[x][y] == -1:
            valor_op += 2

        # eu tinha fixado o limite em 3. agora depende do tamanho do mapa
        # e aqui confiro o que tem na celula, nao so as coordenadas dela
        if x > 0 and self.mapa[x-1][y] != 'X':
            pacote = self.pos_pacote
            if self.encomenda:
                pacote = (x-1, y)
            successors.append(ProblemaEntrega('ir p cima', self.mapa, (x-1, y), pacote, self.final, self.encomenda, valor_op))

        if x < n-1 and self.mapa[x+1][y] != 'X':
            pacote = self.pos_pacote
            if self.encomenda:
                pacote = (x+1, y)
            successors.append(ProblemaEntrega('ir p baixo', self.mapa, (x+1, y), pacote, self.final, self.encomenda, valor_op))

        if y > 0 and self.mapa[x][y-1] != 'X':
            pacote = self.pos_pacote
            if self.encomenda:
                pacote = (x, y-1)
            successors.append(ProblemaEntrega('ir p esq', self.mapa, (x, y-1), pacote, self.final, self.encomenda, valor_op))

        if y < n-1 and self.mapa[x][y+1] != 'X':
            pacote = self.pos_pacote
            if self.encomenda:
                pacote = (x, y+1)
            successors.append(ProblemaEntrega('ir p dir', self.mapa, (x, y+1), pacote, self.final, self.encomenda, valor_op))

        # chegar no pacote nao significa pegar. faltava separar essa acao na prova
        if self.pos_pessoa == self.pos_pacote and not self.encomenda:
            successors.append(ProblemaEntrega('pegar pacote', self.mapa, self.pos_pessoa, self.pos_pacote, self.final, True, valor_op))

        # pelo enunciado da pra largar em qualquer celula, mas so no destino resolve
        if self.encomenda:
            successors.append(ProblemaEntrega('entregar pacote', self.mapa, self.pos_pessoa, self.pos_pessoa, self.final, False, valor_op))

        # antes eu devolvia so (x, y). agora cada sucessor e um objeto da classe
        # bater na parede nao entra aqui pq nao muda o estado e ainda gasta uma acao
        return successors

    def is_goal(self):
        # eu tinha olhado a pessoa no destino com a mochila, mas ainda faltava entregar
        return self.pos_pacote == self.final and not self.encomenda

    def description(self):
        return 'Problema de entrega de pacote'

    def cost(self):
        return self.valor_op

    def env(self):
        # nao precisa guardar Y por onde a pessoa passou, como eu fiz na prova
        # o que importa aqui e onde os dois estao e se ela esta carregando
        return str(self.pos_pessoa) + '#' + str(self.pos_pacote) + '#' + str(self.encomenda)

    def h(self):
        if self.is_goal():
            return 0

        x, y = self.pos_pessoa
        px, py = self.pos_pacote
        fx, fy = self.final

        # eu tinha explicado "quanto mais perto, menor", mas faltava fazer a conta
        if self.encomenda:
            # ja pegou, entao falta chegar no destino e entregar
            return abs(x-fx) + abs(y-fy) + 1

        # sem o pacote, primeiro precisa buscar ele. o +2 e pegar e entregar
        distancia_pacote = abs(x-px) + abs(y-py)
        distancia_final = abs(px-fx) + abs(py-fy)
        # nao conto obstaculos e pedagios aqui pra nao chutar um custo maior que o real
        return distancia_pacote + distancia_final + 2


# esse pedacinho ficou aqui no mesmo arquivo pra nao precisar de outro .py
# evita repetir caminho a toa e aceita trocar um caminho caro por um mais barato
# o A* da versao 0.3.9 nao faz essas duas coisas juntas na chamada padrao
class BuscaEntrega(AEstrela):

    def search(self, estado_inicial):
        inicial = Node(estado_inicial, None)
        abertos = [inicial]
        custos = {estado_inicial.env(): 0}

        while abertos:
            abertos.sort(key=lambda no: no.f(), reverse=True)
            atual = abertos.pop()

            if atual.g > custos[atual.state.env()]:
                continue

            if atual.state.is_goal():
                return atual

            for estado in atual.state.successors():
                novo = Node(estado, atual)
                chave = estado.env()

                if chave not in custos or novo.g < custos[chave]:
                    custos[chave] = novo.g
                    abertos.append(novo)

        return None


def main():
    print('Busca A Estrela - Entrega de pacote')

    while True:
        try:
            n = int(input('Qual o tamanho do grid? '))
            if n > 0:
                break
            print('Coloca um tamanho maior que zero.')
        except ValueError:
            print('Coloca um numero inteiro, tipo 4 ou 10.')

    mapa = []
    posicoes = []
    for x in range(n):
        linha = []
        for y in range(n):
            linha.append(0)
            posicoes.append((x, y))
        mapa.append(linha)

    if n == 1:
        # nesse caso so tem uma celula, entao o pacote ja esta no destino
        inicio = pacote = final = (0, 0)
    else:
        inicio, pacote, final = random.sample(posicoes, 3)

    livres = []
    for posicao in posicoes:
        if posicao != inicio and posicao != pacote and posicao != final:
            livres.append(posicao)

    quantidade = random.randint(0, len(livres))
    obstaculos = random.sample(livres, quantidade)
    for x, y in obstaculos:
        mapa[x][y] = 'X'

    livres = []
    for x, y in posicoes:
        if mapa[x][y] != 'X':
            livres.append((x, y))

    quantidade = random.randint(0, len(livres))
    pedagios = random.sample(livres, quantidade)
    for x, y in pedagios:
        mapa[x][y] = -1

    print(f'\nGrid: {n} x {n}')
    print('As posicoes sao (linha, coluna), comecando no zero.')
    print(f'Pessoa: {inicio}')
    print(f'Pacote: {pacote}')
    print(f'Destino: {final}')
    print(f'Obstaculos: {obstaculos}')
    print(f'Pedagios: {pedagios}')

    # pode sair um mapa sem solucao mesmo, nao fico sorteando ate dar certo
    state = ProblemaEntrega('', mapa, inicio, pacote, final)
    algorithm = BuscaEntrega()

    start = time.time()
    result = algorithm.search(state)
    end = time.time()

    if result is not None:
        print('\nAchou!')
        if result.depth == 0:
            print('O pacote ja esta no destino.')
        else:
            print(result.show_path().lstrip(' ;'))
        print(f'\nCusto Total: {result.g}')
        print(f'Tempo: {end-start:.4f}s')
    else:
        print('\nNao existe solucao pra esse mapa.')


if __name__ == '__main__':
    main()
