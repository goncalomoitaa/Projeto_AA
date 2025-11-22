import random
import sys
import time
from typing import List
import json

from Agente import Agente
from Ambiente import Ambiente


class MotorDeSimulacao:

    def __init__(self, agentes: List[Agente], ambiente: Ambiente):
        self.agentes = agentes
        self.ambiente = ambiente
        self.passos = 200

    def cria(self, nome_do_ficheiro_parametros: str):
        try:
            with open(nome_do_ficheiro_parametros, 'r', encoding="utf-8") as file:
                parametros = json.load(file)
                sizeX = parametros.get('sizeX')
                sizeY = parametros.get('sizeY')
                self.ambiente = Ambiente(sizeX, sizeY)
                self.passos = parametros.get('passos')
                nomes_agentes = parametros.get('nome_agentes')
                num_obstaculos = parametros.get('num_obstaculos')
                for i in range(num_obstaculos):
                    while True:
                        x = random.randint(0, sizeX - 1)
                        y = random.randint(0, sizeY - 1)
                        if (x,y) not in self.listaAgentes() and (x, y) != self.ambiente.farol and (x,y) not in self.ambiente.obstaculos:
                            self.ambiente.obstaculos.append((x,y))
                            break
                for nome in nomes_agentes:
                    agente = Agente(nome, 0, 0)
                    while True:
                        x = random.randint(0, sizeX - 1)
                        y = random.randint(0, sizeY - 1)
                        if (x,y) not in self.ambiente.obstaculos and (x, y) != self.ambiente.farol:
                            agente.x = x
                            agente.y = y
                            break
                    self.agentes.append(agente)
                    self.ambiente.agentes.append(agente)
        except Exception as e:
            print(f"Erro ao ler o ficheiro JSON: {e}", file=sys.stderr)
            return self
        return self

    def listaAgentes(self):
        return self.agentes

    def executa(self):
        for passo in range(self.passos):
            for agente in self.listaAgentes():
                self.ambiente.observacaoPara(agente)
                print(f"Agente {agente.nome} na posicao ({agente.x}, {agente.y}) com observacao: {agente.observacaoCurrente}")#eleminar futuramente esta parte
                accao = agente.age()
                self.ambiente.agir(accao, agente)
                if(agente.x, agente.y) == self.ambiente.farol: #eleminar futuramente esta parte
                    print("CHEGOU AO FAROL!!!!")
                    self.ambiente.farol = None
                    self.drawingWorld()
                    return
                self.drawingWorld()
                time.sleep(1)

    def drawingWorld(self):
        world = [[" . " for _ in range(self.ambiente.sizeX)] for _ in range(self.ambiente.sizeY)]
        if self.ambiente.farol is not None:
            fx, fy = self.ambiente.farol
            world[fy][fx] = " T "
        for agente in self.listaAgentes():
            world[agente.y][agente.x] = f" {agente.nome} "
        for obstaculo in self.ambiente.obstaculos:
            world[obstaculo[1]][obstaculo[0]] = " # "
        for w in world:
            print("".join(w))
        print()

if __name__ == "__main__":
    sim = MotorDeSimulacao([], None).cria("world.json")
    sim.executa()






