import random
import numpy as np

from agentes.AccaoMover import AccaoMover
from politicas.Politica import Politica

class PoliticaQLearning(Politica):

    def __init__(self, learning_rate=0.7, discount_factor=0.95, exploration_rate=1.0, epsilon_decay=0.90):
        super().__init__()
        self.alpha = learning_rate #α
        self.gamma = discount_factor #γ
        self.epsilon = exploration_rate #ε
        self.epsilon_decay = epsilon_decay
        self.q_table = {} # Tabela Q
        self.accoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.ultimo_estado = None
        self.ultima_accao = None
        self.tem_carga = False
        self.items_recolhidos = 0
        self.passo_atual = 0
        self.acabou = False
        self.objetivo = 0

    def pegar_estado(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0 for _ in range(len(self.accoes))]
        return self.q_table[state]

    def escolher_accao(self, agente):
        estado = (agente.x, agente.y, self.tem_carga, self.items_recolhidos)
        if random.random() < self.epsilon:
            accao = random.randint(0, len(self.accoes) - 1)
        else:
            q_valores = self.pegar_estado(estado)
            max_q = np.max(q_valores)
            best_accao = [i for i, q in enumerate(q_valores) if q == max_q]
            accao = random.choice(best_accao)
        self.ultimo_estado = estado
        self.ultima_accao = accao
        self.passo_atual += 1
        return AccaoMover(self.accoes[accao])

    def aprender(self, agente, recompensa):
        if self.ultimo_estado is None:
            return
        estado_atual = (agente.x, agente.y, self.tem_carga, self.items_recolhidos)
        q_antigo = self.pegar_estado(self.ultimo_estado)[self.ultima_accao]
        max_q_novo = np.max(self.pegar_estado(estado_atual))
        q_novo = (1 - self.alpha) * q_antigo + self.alpha * (recompensa + self.gamma * max_q_novo)
        self.q_table[self.ultimo_estado][self.ultima_accao] = q_novo

    def fim_episodio(self):
        if self.epsilon > 0.01:
            self.epsilon *= self.epsilon_decay
        self.ultimo_estado = None
        self.ultima_accao = None
        self.tem_carga = False
        self.items_recolhidos = 0
        self.passo_atual = 0
        self.acabou = False
