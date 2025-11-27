from Politica import Politica

class PoliticaAleatoria(Politica):
    def __init__(self, acciones):
        self.acciones = acciones

    def seleccionar_accion(self, estado):
        pass