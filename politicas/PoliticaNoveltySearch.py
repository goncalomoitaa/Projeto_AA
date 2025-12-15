import random

from agentes.AccaoMover import AccaoMover
from politicas.Politica import Politica


class PoliticaNoveltySearch(Politica):

    def __init__(self, genotipo=None, num_passos = 0):
        super().__init__()
        self.lista_accoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.num_passos = num_passos
        self.acabou = False
        if genotipo: #Todo vai ter o depositar e recolher?
            self.genotipo = genotipo #recebe os genes do pai
        else:
            self.genotipo = [random.choice(self.lista_accoes) for _ in range(self.num_passos)] #na primeira geração como não tem genes o movimento tem que ser aleatório
        self.comportamento = set() #guarda para ver se é novidade ou comportamento repetido(guarda posições visitadas não repetidas)
        self.caminho = [] #guarda o caminho percorrido nessa geração
        #variáveis que criamos para ver a evolucação entre gerações
        self.fitness_objetivo = 0.0
        self.objetivo = 0
        self.novelty_score = 0
        #Todo definimos as métricas todas mesmo as que façam parte só de um ambiente?
        self.passo_atual = 0
        self.items_recolhidos = 0
        self.score_recursos = 0 #mudar

    def reset(self): #única coisa que não da reset é o genótipo, ou seja, se o caminho for bom guarda ele e já nasce a saber
        self.passo_atual = 0
        self.comportamento = set()
        self.caminho = []
        self.items_recolhidos = 0
        self.objetivo = 0
        self.score_recursos = 0

    def escolher_accao(self, agente):
            pos_atual = (agente.x, agente.y)
            self.comportamento.add(pos_atual) #quanto mais tiver maior a novidade
            self.caminho.append(pos_atual)
            if self.passo_atual < len(self.genotipo): #caso ainda ainda tenha algo genético usa para se mover
                direcao = self.genotipo[self.passo_atual]
                self.passo_atual += 1
                return AccaoMover(direcao)
            self.passo_atual += 1
            return AccaoMover((0,0)) #falta por +=1?

    def mutar(self, taxa_mutacao): #altera os genes com base na taxa, levando a zonas inexploradas
        for i in range(len(self.genotipo)):
            if random.random() < taxa_mutacao:
                self.genotipo[i] = random.choice(self.lista_accoes)

    @staticmethod
    def crossover(parent1, parent2):#combina genótipo de dois pais para criar os filhos
        #min entre o p1 e p2?
        point = random.randint(1, len(parent1.genotipo) - 1)
        filho1_geno = parent1.genotipo[:point] + parent2.genotipo[point:]
        filho2_geno = parent2.genotipo[:point] + parent1.genotipo[point:]
        return PoliticaNoveltySearch(filho1_geno), PoliticaNoveltySearch(filho2_geno)

    def calcular_fitness(self):
        return self.objetivo

    @staticmethod
    def distancia_jaccard(set1, set2):  # mede o quão diferente são os dois caminhos
        intersecao = len(set1 & set2)
        uniao = len(set1 | set2)
        return 1 - (intersecao / uniao) if uniao != 0 else 0

    @staticmethod
    def computar_novelty(comportamento_corrente, arquivo, k):  # calcula a novidade para os k vizinhos mais próximos
        if not arquivo:
            return 1.0
        distancias = [PoliticaNoveltySearch.distancia_jaccard(comportamento_corrente, b) for b in arquivo]  # compara o caminho feito pelo o agente com o da memória passada
        distancias.sort()
        if len(distancias) >= k:
            return sum(distancias[:k]) / k
        else:
            return sum(distancias) / len(distancias)

    @staticmethod
    def seleciona_pais(populacao, tamanho_torneio):
        torneio = random.sample(populacao, tamanho_torneio)
        torneio.sort(key=lambda x: x.fitness_objetivo, reverse=True)
        return torneio[0]