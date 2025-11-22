import random

from AccaoMover import AccaoMover
from Observacao import Observacao
import Sensor
from SensorAgente import SensorAgente
from SensorFarol import SensorFarol
from SensorObstaculo import SensorObstaculo

# from abc import ABC, abstractmethod

class Agente:

    def __init__(self, nome: str, x: int, y: int):
        self.nome = nome
        self.x = x
        self.y = y
        self.sensoresAgente = [SensorObstaculo(), SensorAgente(), SensorFarol()]
        self.observacaoCurrente = None

    def observacao(self, obs: Observacao):
        self.observacaoCurrente = obs

    def instala(self, sensor: Sensor):
        self.sensoresAgente.append(sensor)

    def age(self):
        obs = self.observacaoCurrente.sensores
        obs_farol = obs.get("SensorFarol")
        if obs_farol and "farol" in obs_farol:
            pos_x, pos_y = obs_farol["farol"]
            dx = pos_x - self.x
            dy = pos_y - self.y
            i = 0 if dx == 0 else (1 if dx > 0 else -1)
            j = 0 if dy == 0 else (1 if dy > 0 else -1)
            print(self.observacaoCurrente.sensores.get("SensorObstaculo"))
            if self.observacaoCurrente.sensores.get("SensorObstaculo").get((self.x + i, self.y + j)) != "obstaculo":
                return AccaoMover((i, j))
        obs_obs = obs.get("SensorObstaculo")
        if obs_obs != {}:
            direcoes = [(-1,0), (1,0), (0,-1), (0,1)]
            random.shuffle(direcoes)
            for direcao in direcoes:
                nova_pos = (self.x + direcao[0], self.y + direcao[1])
                if obs_obs.get(nova_pos) == "vazio":
                    return AccaoMover(direcao)
        return AccaoMover((0,0))


    def get_pos(self):
        return self.x, self.y

    def get_nome(self):
        return self.nome

if __name__ == "__main__":
    agente = Agente("A", 0, 0)
    observacao = Observacao(agente)
    # observacao.adiciona_sensor("distancia", {'farol': (0,2)})
    observacao.adiciona_sensor("outro_sensor", {(1,0): "obstaculo"})
    x = observacao.sensores.get("outro_sensor").get((1,0))
    print(x)  # Output: farol



