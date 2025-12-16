from agentes.Accao import Accao
from ambientes.Ambiente import Ambiente
from agentes.AccaoMover import AccaoMover
from agentes.AgenteFarol import AgenteFarol


class AmbienteFarol(Ambiente):

    def __init__(self, sizeX, sizeY, farol):
        super().__init__(sizeX, sizeY)
        self.farol = farol
        self.objetivos = [farol]

    def agir(self, accao: Accao, agente: AgenteFarol):
        if isinstance(accao, AccaoMover):
            dx, dy = accao.direcao

            # 1. Penalidade por ficar parado
            if (dx, dy) == (0, 0):
                agente.avaliacaoEstadoAtual(-5)
                return
            else:
                x = agente.x + dx
                y = agente.y + dy

                # 2. Recompensa Final (Chegou ao Farol)
                if (x, y) == self.farol:
                    agente.x = x
                    agente.y = y
                    agente.avaliacaoEstadoAtual(100)  # Recompensa alta!
                    agente.politica.acabou = True
                    return

                # 3. Penalidades por Colisões (Obstáculos/Agentes/Limites)
                if (x, y) in self.obstaculos:
                    agente.avaliacaoEstadoAtual(-5)
                    return
                for outro_agente in self.agentes:
                    if outro_agente != agente and (x, y) == (outro_agente.x, outro_agente.y):
                        agente.avaliacaoEstadoAtual(-5)
                        return
                if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
                    agente.avaliacaoEstadoAtual(-5)
                    return

                # 4. MOVIMENTO VÁLIDO COM RECOMPENSA DE DISTÂNCIA
                else:
                    # A. Calcular distâncias (Manhattan: |x1-x2| + |y1-y2|)
                    fx, fy = self.farol
                    dist_antiga = abs(agente.x - fx) + abs(agente.y - fy)
                    dist_nova = abs(x - fx) + abs(y - fy)

                    # B. Calcular a Recompensa (Shaped Reward)
                    # dist_antiga - dist_nova será:
                    #    +1 se ele se aproximou (ex: estava a 10m, agora está a 9m)
                    #    -1 se ele se afastou (ex: estava a 10m, agora está a 11m)
                    #     0 se manteve a distância (movimento lateral raro em Manhattan puro)
                    recompensa_progresso = (dist_antiga - dist_nova)

                    # C. Aplicar Recompensa
                    # Mantemos um pequeno custo de passo (-0.1) para ele não andar em círculos
                    # Total: Se aproximar ganha 0.9. Se afastar perde 1.1.
                    agente.avaliacaoEstadoAtual(recompensa_progresso - 0.1)

                    # Atualizar posição
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