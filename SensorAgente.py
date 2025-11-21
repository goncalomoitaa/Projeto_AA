from Sensor import Sensor


class SensorAgente(Sensor):

    def __init__(self):
        super().__init__("SensorAgente", 1)

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
                    for outro_agente in ambiente.agentes:
                        if pos == (outro_agente.x, outro_agente.y) and outro_agente != agente:
                            obs[pos] = outro_agente.nome
        return obs
