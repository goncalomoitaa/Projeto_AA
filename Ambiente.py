
from Agente import Agente
from Observacao import Observacao


class Ambiente:

    def __init__(self, sizeX, sizeY):
        self.sizeX = sizeX
        self.sizeY = sizeY
        # self.recursos = []
        self.obstaculos = []
        self.agentes = []
        self.farol = (1, 1)

    def observacaoPara(self, agente):
        obs = Observacao(agente)
        for sensor in agente.sensores:
            l = sensor.leituraAgente(self, agente)
            obs.adiciona_sensor(sensor.nomeSensor, l)
        agente.observacao(obs)
        return obs

    def agir(self, dx, dy, agente: Agente):
        x = agente.x + dx
        y = agente.y + dy
        if (x, y) in self.obstaculos:
            return
        for outro_agente in self.agentes:
            if outro_agente != agente and (x, y) == (outro_agente.x, outro_agente.y):
                return
        if x < 0 or x >= self.sizeX:
            return
        if y < 0 or y >= self.sizeY:
            return
        else:
            agente.x = x
            agente.y = y





