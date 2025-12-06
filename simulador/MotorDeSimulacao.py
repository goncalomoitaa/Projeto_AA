import sys
import time
from typing import List
import json

from agentes.Agente import Agente
from agentes.AgenteRecolecao import AgenteRecolecao
from agentes.SensorVisao import SensorVisao
from ambientes.Ambiente import Ambiente
from ambientes.AmbienteFarol import AmbienteFarol
from agentes.AgenteFarol import AgenteFarol
from ambientes.AmbienteRecolecao import AmbienteRecolecao


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
                if ambiente == "Ambiente Farol":
                    farol = parametros.get('farol')
                    self.ambiente = AmbienteFarol(sizeX, sizeY, (farol[0], farol[1]))
                    tipo_agente = AgenteFarol
                if ambiente == "Ambiente Recolecao":
                    self.ambiente = AmbienteRecolecao(sizeX, sizeY, [], [])
                    ninhos = parametros.get('ninhos')
                    for pos in ninhos:
                        self.ambiente.ninhos.append((pos[0], pos[1]))
                    recursos = parametros.get('recursos')
                    for recurso in recursos:
                        self.ambiente.recursos.append(recurso)
                    tipo_agente = AgenteRecolecao
                self.passos = parametros.get('passos')
                lista_agentes = parametros.get('agentes')
                obstaculos = parametros.get('obstaculos')
                politica = parametros.get('politica')
                for pos in obstaculos:
                        self.ambiente.obstaculos.append((pos[0], pos[1]))
                for ag in lista_agentes:
                    nome_agente = ag['nome_agente']
                    pos_ag = ag['pos_agente']
                    agente = tipo_agente(nome_agente, pos_ag[0], pos_ag[1])
                    agente.setPolitica(politica)
                    agente.instala(SensorVisao())
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
                        self.ambiente.farol = None #onde fica?
                        self.ambiente.drawingWorld()
                        return
                if isinstance(self.ambiente, AmbienteRecolecao):
                    print(f"points: {self.ambiente.pontos}")
                self.ambiente.drawingWorld()
                time.sleep(1)

if __name__ == "__main__":
    sim = MotorDeSimulacao([], None).cria("simulador/mundoFarol.json")
    sim.executa()






