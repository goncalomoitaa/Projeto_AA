import random
import sys
import time
from typing import List
import json

from Agente import Agente
from AgenteFarol import AgenteFarol
from Ambiente import Ambiente
from AmbienteFarol import AmbienteFarol


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
                ambiente = parametros.get('ambiente')
                x = random.randint(0, sizeX - 1)
                y = random.randint(0, sizeY - 1)
                if ambiente == "Ambiente Farol":
                    self.ambiente = AmbienteFarol(sizeX, sizeY, (x, y))
                    tipo_agente = AgenteFarol
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
                    agente = tipo_agente(nome, 0, 0)
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
                if isinstance(self.ambiente, AmbienteFarol):
                    if(agente.x, agente.y) == self.ambiente.farol:
                        print("CHEGOU AO FAROL!!!!")
                        self.ambiente.farol = None
                        self.ambiente.drawingWorld()
                        return
                self.ambiente.drawingWorld()
                time.sleep(1)

if __name__ == "__main__":
    sim = MotorDeSimulacao([], None).cria("world.json")
    sim.executa()






