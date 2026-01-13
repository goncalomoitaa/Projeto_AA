class Observacao:

    def __init__(self, agente):
        self.agente = agente
        self.sensores = {}

    def adiciona_sensor(self, nome_sensor, leitura):
        self.sensores[nome_sensor] = leitura

    def get_sensores(self):
        return self.sensores

    def __str__(self):
        return str(self.sensores)


