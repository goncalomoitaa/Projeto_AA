import random
import sys
import time
from typing import List
import json

from Agente import Agente
from Ambiente import Ambiente
from SensorDistanciaVisao import SensorDistanciaVisao


class MotorDeSimulacao:

    def __init__(self, agentes: List[Agente], ambiente: Ambiente):
        self.agentes = agentes
        self.ambiente = ambiente
        self.passo = 200

    def cria(self, nome_do_ficheiro_parametros: str):
        try:
            with open(nome_do_ficheiro_parametros, 'r', encoding="utf-8") as file:
                parametros = json.load(file)
                sizeX = parametros.get('sizeX')
                sizeY = parametros.get('sizeY')
                self.ambiente = Ambiente(sizeX, sizeY)
                self.passo = parametros.get('passos')
                nomes_agentes = parametros.get('nome_agentes')
                num_obstaculos = parametros.get('num_obstaculos')
                for i in range(num_obstaculos):
                    while True:
                        x = random.randint(0, sizeX - 1)
                        y = random.randint(0, sizeY - 1)
                        if (x,y) not in self.agentes and (x, y) != self.ambiente.farol:
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
        for passos in range(self.passo):
            for agente in self.agentes:
                self.ambiente.observacaoPara(agente)
                print(f"{agente.nome}-{agente.get_pos()} {agente.observacaoCurrente}")
                dx, dy = agente.age()
                self.ambiente.agir(dx, dy, agente)
                if(agente.x, agente.y) == self.ambiente.farol: #eleminar futuramente esta parte
                    print("CHEGOU AO FAROL!!!!")
                    self.ambiente.farol = None
                    return
                self.drawingWorld()
                time.sleep(1)

    def drawingWorld(self):
        world = [["." for _ in range(self.ambiente.sizeX)] for _ in range(self.ambiente.sizeY)]
        if self.ambiente.farol is not None:
            fx, fy = self.ambiente.farol
            world[fy][fx] = "T"
        for agente in self.agentes:
            world[agente.y][agente.x] = agente.nome
        for obstaculo in self.ambiente.obstaculos:
            world[obstaculo[1]][obstaculo[0]] = "#"
        for l in world:
            print("".join(l))
        print()

if __name__ == "__main__":
    sim = MotorDeSimulacao([], None).cria("world.json")
    sim.executa()






