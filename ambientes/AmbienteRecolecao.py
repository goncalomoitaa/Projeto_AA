from agentes.AgenteRecolecao import AgenteRecolecao
from ambientes.Ambiente import Ambiente
from agentes.AccaoMover import AccaoMover
from agentes.AccaoRecolher import AccaoRecolher
from agentes.AccaoDepositar import AccaoDepositar


class AmbienteRecolecao(Ambiente):

    def __init__(self, sizeX, sizeY, recursos, ninhos):
        super().__init__(sizeX, sizeY)
        self.recursos = recursos
        self.ninhos = ninhos
        self.recursos_depositados = 0
        self.recursos_na_mochila = 0
        self.numero_recursos = len(recursos)

    def agir(self, accao, agente: AgenteRecolecao):
        print(f"Recursos na mochila: {agente.mochila}" )
        print(f"Recursos depositados: {self.recursos_depositados}" )
        if isinstance(accao, AccaoMover):
            dx, dy = accao.direcao
            if (dx, dy) == (0, 0):
                return
            else:
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

        if isinstance(accao, AccaoRecolher):
            for rec in self.recursos:
                if [agente.x, agente.y] == rec["pos"]:
                    agente.mochila += 1
                    self.recursos.remove(rec)
                    return

        if isinstance(accao, AccaoDepositar):
            if (agente.x, agente.y) in self.ninhos:
                self.recursos_depositados += agente.mochila
                agente.mochila = 0
                # self.ninhos.remove((agente.x, agente.y))
                #o ninho não desaparece depois de depositar
                return


    def drawingWorld(self):
        world = [[" . " for _ in range(self.sizeX)] for _ in range(self.sizeY)]
        for ninho in self.ninhos:
            world[ninho[1]][ninho[0]] = " N "
        for recurso in self.recursos:
            pos = recurso["pos"]
            world[pos[1]][pos[0]] = " R "
        for agente in self.agentes:
            world[agente.y][agente.x] = f" {agente.nome} "
        for obstaculo in self.obstaculos:
            world[obstaculo[1]][obstaculo[0]] = " # "
        for w in world:
            print("".join(w))
        print()

    def getItem(self, x, y):
        if (x, y) in self.obstaculos:
            return "OBSTACULO"
        if (x, y) in self.ninhos:
            return "NINHO"
        for rec in self.recursos:
            if [x, y] == rec["pos"]:
                return "RECURSO"
        else:
            return "VAZIO"

