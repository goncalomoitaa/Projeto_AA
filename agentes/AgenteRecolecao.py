import random

from agentes.AccaoDepositar import AccaoDepositar
from agentes.AccaoMover import AccaoMover
from agentes.AccaoRecolher import AccaoRecolher
from agentes.Agente import Agente


class AgenteRecolecao(Agente):

    def __init__(self, nome, x, y):
        super().__init__(nome, x, y)
        self.mochila = 0

    def age(self):
        obs = self.observacaoCurrente.sensores["SensorDistancia"]
        pos = (self.x, self.y)
        obj = obs.get(pos)
        if obj == "NINHO":
            return AccaoDepositar()
        if obj == "RECURSO":
            return AccaoRecolher()
        return self.politica.escolher_accao(self)

    def avaliacaoEstadoAtual(self, recompensa):
        self.politica.objetivo += recompensa
        self.politica.items_recolhidos += 1

