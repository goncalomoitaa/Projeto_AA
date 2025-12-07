from abc import ABC, abstractmethod

from agentes.Observacao import Observacao


class Politica(ABC):

    def Politica(self):
        pass
    
    @abstractmethod
    def escolher_accao(self, agente, observacao: Observacao):
        pass