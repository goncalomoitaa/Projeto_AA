from abc import ABC, abstractmethod

class Sensor(ABC):

    def __init__(self, nomeSensor):
        self.nomeSensor = nomeSensor

    @abstractmethod
    def leituraAgente(self, ambiente, agente):
        pass



