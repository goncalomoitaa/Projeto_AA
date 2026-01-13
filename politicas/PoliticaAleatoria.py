import random

from agentes.AccaoMover import AccaoMover
from politicas.Politica import Politica

class PoliticaAleatoria(Politica):

    def __init__(self):
        super().__init__()
        self.acabou = False
        self.objetivo = 0
        self.passo_atual = 0
        self.items_recolhidos = 0

    def escolher_accao(self, agente):
        obs = agente.observacaoCurrente.sensores["SensorDistancia"]
        obj = [] #estado do objetivo que é visivel para o agente
        for i in self.objetivos:
            if tuple(i) in obs:
                obj.append(tuple(i))
        if agente.pegos > 0: #se tiver pego algum recurso adiciona aos objetivos os ninhos
            for j in self.ninhos:
                if tuple(j) in obs:
                    obj.append(tuple(j))
        if obj:
            alvo = min(
                obj,
                key=lambda pos: abs(pos[0] - agente.x) + abs(pos[1] - agente.y) #distancia de Manhattan
            )  #escolhe oque estiver mais próximo
            dx = alvo[0] - agente.x
            dy = alvo[1] - agente.y
            i = 0 if dx == 0 else (1 if dx > 0 else -1)
            j = 0 if dy == 0 else (1 if dy > 0 else -1)
            if abs(dx) >= abs(dy): #vai na direção que for maior a distância
                tentativas = [(i, 0), (0, j)]
            else :
                tentativas = [(0, j), (i, 0)]
            for x, y in tentativas:
                if dx == 0 and dy == 0:
                    continue
                nova_pos = (agente.x + dx, agente.y + dy)
                obstaculo = (obs.get(nova_pos) == "OBSTACULO")
                if not obstaculo:
                    self.passo_atual += 1
                    return AccaoMover((x, y))
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)] #anda aleatoriamente
        random.shuffle(direcoes)
        for di, dj in direcoes:
            nova_pos = (agente.x + di, agente.y + dj)
            if agente.observacaoCurrente.sensores["SensorDistancia"].get(nova_pos) != "OBSTACULO":
                self.passo_atual += 1
                return AccaoMover((di, dj))
        self.passo_atual += 1
        return AccaoMover((0, 0))


