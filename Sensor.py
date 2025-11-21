from abc import ABC, abstractmethod

class Sensor(ABC):

    def __init__(self, nomeSensor, distancia):
        self.nomeSensor = nomeSensor
        self.distancia = distancia

    def set_distancia(self, distancia):
        self.distancia = distancia

    @abstractmethod
    def leituraAgente(self, ambiente, agente):
        pass



