from agentes.AgenteRecolecao import AgenteRecolecao
from ambientes.Ambiente import Ambiente
from agentes.AccaoMover import AccaoMover
from agentes.AccaoRecolher import AccaoRecolher
from agentes.AccaoDepositar import AccaoDepositar


class AmbienteRecolecao(Ambiente):

    def __init__(self, sizeX, sizeY, recursos, ninhos):
        super().__init__(sizeX, sizeY)
        self.ninhos = ninhos
        self.recursos = recursos
        self.pontos = 0
        self.objetivos = [tuple(item["pos"]) for item in recursos]

    def agir(self, accao, agente: AgenteRecolecao):
        # print(f"pontos agente: {agente.mochila}" )
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
                    agente.avaliacaoEstadoAtual(30)
                    ponto = rec["valor"]
                    agente.mochila += ponto
                    self.recursos.remove(rec)
                    return
        if isinstance(accao, AccaoDepositar):
            if (agente.x, agente.y) in self.ninhos:
                agente.avaliacaoEstadoAtual(100)
                self.pontos += agente.mochila
                agente.mochila = 0
                self.ninhos.remove((agente.x, agente.y))
                if(len(self.ninhos) == 0):
                    agente.politica.acabou = True
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
        if (x, y) in self.agentes:
            return "AGENTE"
        if (x, y) in self.ninhos:
            return "NINHO"
        for rec in self.recursos:
            if [x, y] == rec["pos"]:
                return "RECURSO"
        else:
            return "VAZIO"

