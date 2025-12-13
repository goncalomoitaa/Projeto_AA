from agentes.Accao import Accao
from ambientes.Ambiente import Ambiente
from agentes.AccaoMover import AccaoMover
from agentes.AgenteFarol import AgenteFarol


class AmbienteFarol(Ambiente):

    def __init__(self, sizeX, sizeY, farol):
        super().__init__(sizeX, sizeY)
        self.farol = farol

    def agir(self, accao: Accao, agente: AgenteFarol):
        if isinstance(accao, AccaoMover):
            dx, dy = accao.direcao
            if(dx, dy) == (0, 0):
                # agente.avaliacaoEstadoAtual(-1)
                return
            else:
                x = agente.x + dx
                y = agente.y + dy
                if(x, y) == self.farol:
                    agente.x = x
                    agente.y = y
                    agente.avaliacaoEstadoAtual(100)
                    return
                if (x, y) in self.obstaculos:
                    agente.avaliacaoEstadoAtual(-5)
                    return
                for outro_agente in self.agentes:
                    if outro_agente != agente and (x, y) == (outro_agente.x, outro_agente.y):
                        agente.avaliacaoEstadoAtual(-5)
                        return
                if x < 0 or x >= self.sizeX:
                    agente.avaliacaoEstadoAtual(-5)
                    return
                if y < 0 or y >= self.sizeY:
                    agente.avaliacaoEstadoAtual(-5)
                    return
                else:
                    agente.avaliacaoEstadoAtual(-1)
                    agente.x = x
                    agente.y = y

    def drawingWorld(self):
        world = [[" . " for _ in range(self.sizeX)] for _ in range(self.sizeY)]
        if self.farol is not None:
            fx, fy = self.farol
            world[fy][fx] = " T "
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
        if (x, y) == self.farol:
            return "FAROL"
        else:
            return "VAZIO"