import math
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

    def calcular_distancia_minima(self, agente):
        x, y = agente.x, agente.y

        if agente.mochila > 0:
            targets = self.ninhos
        else:
            targets = [tuple(r["pos"]) for r in self.recursos]

        if not targets:
            return 0

        min_dist = float('inf')
        for tx, ty in targets:
            dist = abs(tx - x) + abs(ty - y)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def agir(self, accao, agente: AgenteRecolecao):

        if isinstance(accao, AccaoMover):
            dx, dy = accao.direcao
            if (dx, dy) == (0, 0):
                agente.avaliacaoEstadoAtual(-5)
                return

            x_novo = agente.x + dx
            y_novo = agente.y + dy


            if (x_novo < 0 or x_novo >= self.sizeX or
                    y_novo < 0 or y_novo >= self.sizeY or
                    (x_novo, y_novo) in self.obstaculos):

                agente.avaliacaoEstadoAtual(-10)
                return

            for outro in self.agentes:
                if outro != agente and (x_novo, y_novo) == (outro.x, outro.y):
                    agente.avaliacaoEstadoAtual(-10)
                    return

            dist_antes = self.calcular_distancia_minima(agente)

            agente.x = x_novo
            agente.y = y_novo

            dist_depois = self.calcular_distancia_minima(agente)

            if dist_depois < dist_antes:
                agente.avaliacaoEstadoAtual(0.5)
            else:
                agente.avaliacaoEstadoAtual(-2.0)
            return

        if isinstance(accao, AccaoRecolher):
            recurso_alvo = None
            for rec in self.recursos:
                if [agente.x, agente.y] == rec["pos"]:
                    recurso_alvo = rec
                    break

            if recurso_alvo:
                self.recursos.remove(recurso_alvo)
                agente.mochila += recurso_alvo["valor"]

                agente.politica.items_recolhidos += 1
                agente.avaliacaoEstadoAtual(50)
            else:
                agente.avaliacaoEstadoAtual(-5)
            return

        if isinstance(accao, AccaoDepositar):
            pos_atual = [agente.x, agente.y]

            ninho_encontrado = False
            for n in self.ninhos:
                if list(n) == list(pos_atual):
                    ninho_encontrado = True
                    break

            if ninho_encontrado:
                self.pontos += agente.mochila
                agente.mochila = 0

                agente.politica.items_recolhidos += 1
                agente.avaliacaoEstadoAtual(100)

                for i, n in enumerate(self.ninhos):
                    if list(n) == list(pos_atual):
                        del self.ninhos[i]
                        break

                if len(self.ninhos) == 0:
                    agente.politica.acabou = True
                elif len(self.recursos) == 0 and agente.mochila == 0:
                    agente.politica.acabou = True
            else:
                agente.avaliacaoEstadoAtual(-5)
            return

    def drawingWorld(self):
        print(f"pontos: {self.pontos}")
        print(self.objetivos)
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

