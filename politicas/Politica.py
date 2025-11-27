from abc import ABC, abstractmethod

class Politica(ABC):
    
    @abstractmethod
    def escolher_accao(self, estado):
        pass