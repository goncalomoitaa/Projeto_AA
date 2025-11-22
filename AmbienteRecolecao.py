from Ambiente import Ambiente


class AmbienteRecolecao(Ambiente):

    def __init__(self, sizeX, sizeY, recursos, ninhos):
        super().__init__(sizeX, sizeY)
        self.recursos = []
        self.ninhos = []

    def agir(self, accao, agente):
        pass

    def atualizacao(self):
        pass

