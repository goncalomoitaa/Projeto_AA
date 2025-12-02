from agentes.Sensor import Sensor

class SensorVisao(Sensor):

    def __init__(self):
        super().__init__("SensorDistancia",1)

    def leituraAgente(self, ambiente, agente):
        dx = agente.x
        dy = agente.y
        obs = {}
        for d in range(1, self.distancia + 1):
            posCima = (dx, dy + d)
            posBaixo = (dx, dy - d)
            posDireita = (dx + d, dy)
            posEsquerda = (dx - d, dy)
            for pos in [posCima, posBaixo, posDireita, posEsquerda]:
                if (0 <= pos[0] < ambiente.sizeX) and (0 <= pos[1] < ambiente.sizeY):
                    obs[pos] = ambiente.getItem(pos[0], pos[1])
        obs[(dx, dy)] = ambiente.getItem(dx, dy)
        return obs
