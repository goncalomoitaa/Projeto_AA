from Accao import Accao
from AccaoMover import AccaoMover
from Agente import Agente
from Observacao import Observacao


class Ambiente:

    def __init__(self, sizeX, sizeY):
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.obstaculos = []
        self.agentes = []
        self.farol = None
        # self.recursos = []

    def observacaoPara(self, agente):
        obs = Observacao(agente)
        for sensor in agente.sensoresAgente:
            l = sensor.leituraAgente(self, agente)
            obs.adiciona_sensor(sensor.nomeSensor, l)
        agente.observacao(obs)
        return obs

    def agir(self, accao: Accao, agente: Agente):
        if isinstance(accao, AccaoMover):
            dx, dy = accao.direcao
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






