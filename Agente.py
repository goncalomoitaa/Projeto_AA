import random

from Observacao import Observacao
from Sensor import Sensor
from SensorDistanciaVisao import SensorDistanciaVisao

# from abc import ABC, abstractmethod

class Agente:

    def __init__(self, nome: str, x: int, y: int):
        self.nome = nome
        self.x = x
        self.y = y
        self.sensores = [SensorDistanciaVisao()]
        self.observacaoCurrente = None

    def observacao(self, obs: Observacao):
        self.observacaoCurrente = obs

    def instala(self, sensor: Sensor):
        self.sensores.append(sensor)

    def age(self):
        pass



    # def age(self):
    #     movimento = [(0,1), (0,-1), (1,0), (-1,0)]
    #     return random.choice(movimento)

    def get_pos(self):
        return self.x, self.y

    def get_nome(self):
        return self.nome

if __name__ == "__main__":
    agente = Agente("A", 0, 0)
    observacao = Observacao(agente)
    observacao.adiciona_sensor("distancia", {(0,1): 'vazio', (0,2): 'farol'})
    print('farol' in observacao.get_sensores()['distancia'].values())  # Deve imprimir True



