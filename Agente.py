from abc import ABC, abstractmethod

from Observacao import Observacao
import Sensor
from SensorDistancia import SensorDistancia


class Agente(ABC):

    def __init__(self, nome: str, x: int, y: int):
        self.nome = nome
        self.x = x
        self.y = y
        self.sensoresAgente = [SensorDistancia()]
        self.observacaoCurrente = None

    def observacao(self, obs: Observacao):
        self.observacaoCurrente = obs

    def instala(self, sensor: Sensor):
        self.sensoresAgente.append(sensor)

    def get_pos(self):
        return self.x, self.y

    def get_nome(self):
        return self.nome

    @abstractmethod
    def age(self):
        pass



