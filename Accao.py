from abc import ABC, abstractmethod

class Accao(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def executar(self, ambiente, agente):
        pass