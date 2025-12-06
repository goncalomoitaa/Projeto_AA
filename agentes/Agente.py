from abc import ABC, abstractmethod

from agentes.Observacao import Observacao


class Agente(ABC):

    def __init__(self, nome: str, x: int, y: int):
        self.nome = nome
        self.x = x
        self.y = y
        self.sensoresAgente = []
        self.observacaoCurrente = None
        self.politica = None

    def observacao(self, obs: Observacao):
        self.observacaoCurrente = obs

    def instala(self, sensor):
        self.sensoresAgente.append(sensor)

    def get_pos(self):
        return self.x, self.y

    def get_nome(self):
        return self.nome

    def setPolitica(self, p):
        self.politica = p

    @abstractmethod
    def age(self):
        pass



