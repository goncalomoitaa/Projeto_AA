from Sensor import Sensor

class SensorDistanciaVisao(Sensor):

    def __init__(self, distancia = 1):
        super().__init__("distancia")
        self.distancia = distancia

    def set_distancia(self, distancia):
        self.distancia = distancia

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
                    obs[pos] = ambiente.leituraAmbiente(pos)[pos]
        return obs
