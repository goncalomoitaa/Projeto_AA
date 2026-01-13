from abc import ABC, abstractmethod

class Politica(ABC):

    def __init__(self):
        self.objetivos = None
        self.obstaculos = None
        self.ninhos = None
        self.colisoes = 0
    
    @abstractmethod
    def escolher_accao(self, agente):
        pass