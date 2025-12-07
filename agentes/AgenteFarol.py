import random

from agentes.Agente import Agente

class AgenteFarol(Agente):
    def __init__(self, nome, x, y, genotipo=None):
        super().__init__(nome, x, y, genotipo=genotipo)
