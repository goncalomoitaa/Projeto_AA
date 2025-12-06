from abc import ABC, abstractmethod

class Politica(ABC):

    def Policia(self):
        pass
    
    @abstractmethod
    def escolher_accao(self, policia_estado):
        pass