from Sensor import Sensor

class SensorObstaculo(Sensor):

    def __init__(self):
        super().__init__("SensorObstaculo",1)

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
                    if pos in ambiente.obstaculos:
                        obs[pos] = 'obstaculo'
                    elif pos != ambiente.farol and all(pos != (outro_agente.x, outro_agente.y) for outro_agente in ambiente.agentes):
                        obs[pos] = 'vazio'
        return obs
