from ambientes.Ambiente import Ambiente
from agentes.AgenteRecolecao import AgenteRecolecao
from agentes.AccaoMover import AccaoMover
from agentes.AccaoRecolher import AccaoRecolher
from agentes.AccaoDepositar import AccaoDepositar

class AmbienteRecolecao(Ambiente):

    def __init__(self, sizeX, sizeY, recursos, ninhos):
        super().__init__(sizeX, sizeY)
        self.ninhos = ninhos
        self.recursos = recursos
        self.pontos = 0
        self.obstaculos = []
        self.objetivos = [tuple(item["pos"]) for item in recursos]

    def calcular_distancia_minima(self, agente: AgenteRecolecao):
        if agente.mochila > 0: #se tiver já tiver pego recursos, vai priorizar chegar ao ninho
            obj = self.ninhos
        else:
            obj = [tuple(r["pos"]) for r in self.recursos]
        if obj == []:
            return 0
        x, y = agente.x, agente.y
        min_dist = min(abs(tx - x) + abs(ty - y) for tx, ty in obj)
        return min_dist

    def agir(self, accao, agente: AgenteRecolecao):
        if isinstance(accao, AccaoMover):
            dx, dy = accao.direcao
            if (dx, dy) == (0, 0):
                agente.avaliacaoEstadoAtual(-5)
                return
            x = agente.x + dx
            y = agente.y + dy
            if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY or (x, y) in self.obstaculos:
                agente.avaliacaoEstadoAtual(-10)
                return
            for outro in self.agentes:
                if outro != agente and (x, y) == (outro.x, outro.y):
                    agente.avaliacaoEstadoAtual(-10)
                    return
            dist_antes = self.calcular_distancia_minima(agente)
            agente.x = x
            agente.y = y
            dist_depois = self.calcular_distancia_minima(agente)
            if dist_depois < dist_antes:
                agente.avaliacaoEstadoAtual(0.5) #aproximou-se do objetivo
            else:
                agente.avaliacaoEstadoAtual(-2.0)
            return
        if isinstance(accao, AccaoRecolher):
            recurso_recolhido = None
            for rec in self.recursos:
                if [agente.x, agente.y] == rec["pos"]:
                    self.objetivos.remove(agente.get_pos())
                    recurso_recolhido = rec
                    break
            if recurso_recolhido:
                self.recursos.remove(recurso_recolhido)
                agente.mochila += recurso_recolhido["valor"]
                agente.politica.items_recolhidos += 1
                agente.avaliacaoEstadoAtual(50)
            else:
                agente.avaliacaoEstadoAtual(-5)
            return
        if isinstance(accao, AccaoDepositar):
            pos_atual = [agente.x, agente.y]
            ninho = False
            for n in self.ninhos:
                if list(n) == list(pos_atual):
                    ninho = True
                    break
            if ninho:
                self.pontos += agente.mochila
                agente.mochila = 0
                agente.politica.items_recolhidos += 1
                agente.avaliacaoEstadoAtual(100)
                if tuple(pos_atual) in self.ninhos:
                    self.ninhos.remove(tuple(pos_atual))
                if len(self.ninhos) == 0: #se não houver mais ninhos acaba
                    agente.politica.acabou = True
                elif len(self.recursos) == 0 and agente.mochila == 0: #se não houver mais recursos e não tiver nada na mochila acaba
                    agente.politica.acabou = True
            else:
                agente.avaliacaoEstadoAtual(-5)
            return

    def drawingWorld(self):
        print(f"pontos: {self.pontos}")
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

