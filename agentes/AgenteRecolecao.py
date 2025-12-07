from agentes.Agente import Agente
class AgenteRecolecao(Agente):
    def __init__(self, nome, x, y, genotipo=None):
        super().__init__(nome, x, y, genotipo=genotipo)
        self.mochila = 0
        self.capacidade = 1  # ou outro valor se quiseres
