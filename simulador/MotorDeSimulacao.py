import sys
import json
import time
from typing import List

from agentes.Agente import Agente
from agentes.AgenteRecolecao import AgenteRecolecao
from agentes.SensorVisao import SensorVisao
from ambientes.Ambiente import Ambiente
from ambientes.AmbienteFarol import AmbienteFarol
from agentes.AgenteFarol import AgenteFarol
from ambientes.AmbienteRecolecao import AmbienteRecolecao
from politicas.PoliticaAleatoria import PoliticaAleatoria
from politicas.PoliticaNoveltySearch import PoliticaNoveltySearch


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
                politica_nome = parametros.get("politica")

                politica_obj = eval(politica_nome + "()")

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
                    self.ambiente.numero_recursos = len(recursos)

                self.passos = parametros.get('passos')
                lista_agentes = parametros.get('agentes')
                obstaculos = parametros.get('obstaculos')

                for pos in obstaculos:
                    self.ambiente.obstaculos.append((pos[0], pos[1]))

                for ag in lista_agentes:
                    nome_agente = ag['nome_agente']
                    pos_ag = ag['pos_agente']
                    genotipo = ag.get('genotipo')  # pode ser None

                    agente = tipo_agente(nome_agente, pos_ag[0], pos_ag[1], genotipo=genotipo)
                    agente.setPolitica(politica_obj)
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
        # registo de posições visitadas para cada agente (para novelty)
        visitas = {agente.nome: set() for agente in self.listaAgentes()}

        for passo in range(self.passos):
            for agente in self.listaAgentes():
                # regista posição atual
                visitas[agente.nome].add((agente.x, agente.y))

                self.ambiente.observacaoPara(agente)
                accao = agente.age()
                self.ambiente.agir(accao, agente)
                self.ambiente.observacaoPara(agente)

                # print(f"Agente {agente.nome} na posicao ({agente.x}, {agente.y}) com observacao: "
                #       f"{agente.observacaoCurrente}")

                # condição de paragem no Farol
                if isinstance(self.ambiente, AmbienteFarol):
                    if (agente.x, agente.y) == self.ambiente.farol:
                        print("CHEGOU AO FAROL!!!!")
                        self.ambiente.farol = None
                        # self.ambiente.drawingWorld()
                        return visitas  # devolve visitas

                # condição de paragem na Recoleção (se já lá estiveres montado)
                if isinstance(self.ambiente, AmbienteRecolecao):
                    if self.ambiente.recursos_depositados == self.ambiente.numero_recursos:
                        print("TODOS OS RECURSOS FORAM DEPOSITADOS!!!!")
                        # self.ambiente.drawingWorld()
                        return visitas  # devolve visitas

                # self.ambiente.drawingWorld()
                # time.sleep(1)

        # se acabar passos sem condição de paragem, devolve o rasto à mesma
        return visitas


if __name__ == "__main__":
    sim = MotorDeSimulacao([], None).cria("mundoFarol.json")
    resultado = sim.executa()
    print("Resultado:", resultado)

