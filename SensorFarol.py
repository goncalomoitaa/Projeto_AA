from Sensor import Sensor


class SensorFarol(Sensor):

    def __init__(self):
        super().__init__("SensorFarol", 1)

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
                    if pos == ambiente.farol:
                            obs['farol'] = pos
        return obs