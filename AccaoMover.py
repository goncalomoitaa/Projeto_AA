from Accao import Accao


class AccaoMover(Accao):

    def __init__(self, direcao):
        super().__init__()
        self.direcao = direcao