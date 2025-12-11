import random

from agentes.AccaoMover import AccaoMover
from politicas.PoliticaUniversalBase import PoliticaUniversalBase


class PoliticaNoveltySearch(PoliticaUniversalBase):

    def __init__(self, genotipo=None, num_passos = 25):
        super().__init__()
        self.lista_accoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.num_passos = num_passos
        if genotipo:
            self.genotipo = genotipo #recebe os genes do pai
        else:
            self.genotipo = [random.choice(self.lista_accoes) for _ in range(self.num_passos)] #na primeira geração como não tem genes o movimento tem que ser aleatório
        self.passo_atual = 0
        self.comportamento = set() #guarda para ver se é novidade ou comportamento repetido(guarda posições visitadas não repetidas)
        self.caminho = [] #guarda o caminho percorrido nessa geração
        #variáveis que criamos para ver a evolucação entre gerações
        self.fitness_objetivo = 0.0
        self.novelty_score = 0
        #Todo definimos as métricas todas mesmo as que façam parte só de um ambiente?
        self.items_recolhidos = 0
        self.score_recursos = 0 #mudar


    def reset(self): #única coisa que não da reset é o genótipo, ou seja, se o caminho for bom guarda ele e já nasce a saber
        self.passo_atual = 0
        self.comportamento = set()
        self.caminho = []
        self.items_recolhidos = 0
        self.score_recursos = 0

    def escolher_accao(self, agente, observacao):
            ctx = self._extrair_contexto(agente, observacao)
            pos_atual = ctx["pos_actual"] #regista a posição em que está
            self.comportamento.add(pos_atual) #quanto mais tiver maior a novidade
            self.caminho.append(pos_atual)
            accao = None
            accao_imediata = self._accao_imediata(agente, ctx)
            if accao_imediata is not None: #se for recolher ou depositar entra nesse if
                self.items_recolhidos += 1
                accao = accao_imediata
            elif self.passo_atual < len(self.genotipo): #caso ainda ainda tenha algo genético usa para se mover
                direcao = self.genotipo[self.passo_atual]
                nova_pos = (agente.x + direcao[0], agente.y + direcao[1])
                visao = ctx["visao"]
                if visao.get(nova_pos) != "OBSTACULO":
                    accao = AccaoMover(direcao)
                else:
                    accao = AccaoMover((0,0)) #fica parado se for obstáculo
            else:
                accao = AccaoMover((0,0))
            self.passo_atual += 1
            return accao
            #Todo e se for farol?

    def mutar(self, taxa_mutacao): #altera os genes com base na taxa, levando a zonas inexploradas
        for i in range(len(self.genotipo)):
            if random.random() < taxa_mutacao:
                self.genotipo[i] = random.choice(self.lista_accoes)

    @staticmethod
    def crossover(parent1, parent2):#combina genótipo de dois pais para criar os filhos
        point = random.randint(1, len(parent1.genotipo) - 1)
        filho1_geno = parent1.genotipo[:point] + parent2.genotipo[point:]
        filho2_geno = parent2.genotipo[:point] + parent1.genotipo[point:]
        return PoliticaNoveltySearch(filho1_geno), PoliticaNoveltySearch(filho2_geno)

    def calcular_fitness(self):
        return self.items_recolhidos * 100




