import random

from AccaoDepositar import AccaoDepositar
from AccaoMover import AccaoMover
from AccaoRecolher import AccaoRecolher
from Agente import Agente


class AgenteRecolecao(Agente):

    def __init__(self, nome, x, y):
        super().__init__(nome, x, y)
        self.mochila = 3

    def age(self):
        obs = self.observacaoCurrente.sensores["SensorDistancia"]
        for pos, tipo in obs.items():
            pos_x, pos_y = pos
            if self.x == pos_x and self.y == pos_y and tipo == "NINHO":
                return AccaoDepositar()
            if self.x == pos_x and self.y == pos_y and tipo == "RECURSO":
                return AccaoRecolher()
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(direcoes)
        for direcao in direcoes:
            nova_pos = (self.x + direcao[0], self.y + direcao[1])
            if obs.get(nova_pos) != "OBSTACULO":
                return AccaoMover(direcao)
        return AccaoMover((0, 0))

