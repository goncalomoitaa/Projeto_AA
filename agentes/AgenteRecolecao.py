from agentes.AccaoDepositar import AccaoDepositar
from agentes.AccaoRecolher import AccaoRecolher
from agentes.Agente import Agente

class AgenteRecolecao(Agente):

    def __init__(self, nome, x, y):
        super().__init__(nome, x, y)
        self.mochila = 0

    def age(self):
        if hasattr(self.politica, 'tem_carga'): #para o QLearning
            self.politica.tem_carga = (self.mochila > 0)
        obs = self.observacaoCurrente.sensores["SensorDistancia"]
        pos = (self.x, self.y)
        obj = obs.get(pos)
        if obj == "NINHO" and self.mochila > 0:
            return AccaoDepositar()
        if obj == "RECURSO":
            self.pegos += 1
            return AccaoRecolher()
        return self.politica.escolher_accao(self)

