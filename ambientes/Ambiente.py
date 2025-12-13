

from abc import ABC, abstractmethod

from agentes.Accao import Accao
from agentes.Agente import Agente
from agentes.Observacao import Observacao


class Ambiente(ABC):

    def __init__(self, sizeX, sizeY):
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.obstaculos = []
        self.agentes = []

    def observacaoPara(self, agente):
        obs = Observacao(agente)
        for sensor in agente.sensoresAgente:
            l = sensor.leituraAgente(self, agente)
            obs.adiciona_sensor(sensor.nomeSensor, l)
        agente.observacao(obs)
        return obs

    @abstractmethod
    def agir(self, accao: Accao, agente: Agente):
        pass

    @abstractmethod
    def drawingWorld(self):
        pass

    @abstractmethod
    def getItem(self, x, y):
        pass






