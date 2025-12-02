import random

from agentes.AccaoMover import AccaoMover
from agentes.Agente import Agente


class AgenteFarol(Agente):

    def __init__(self, nome, x, y):
        super().__init__(nome, x, y)

    def age(self):
        obs = self.observacaoCurrente.sensores["SensorDistancia"]
        for pos, tipo in obs.items():
            if tipo == "FAROL":
                pos_x, pos_y = pos
                dx = pos_x - self.x
                dy = pos_y - self.y
                i = 0 if dx == 0 else (1 if dx > 0 else -1)
                j = 0 if dy == 0 else (1 if dy > 0 else -1)
                if obs.get((self.x + i, self.y + j)) != "OBSTACULO":
                    return AccaoMover((i, j))
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(direcoes)
        for direcao in direcoes:
            nova_pos = (self.x + direcao[0], self.y + direcao[1])
            if obs.get(nova_pos) == "VAZIO":
                return AccaoMover(direcao)
        return AccaoMover((0,0))