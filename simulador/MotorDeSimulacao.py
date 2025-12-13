import sys
import time
from threading import Thread
from typing import List
import json

from matplotlib import pyplot as plt

from agentes.Agente import Agente
from agentes.AgenteRecolecao import AgenteRecolecao
from agentes.SensorVisao import SensorVisao
from ambientes.Ambiente import Ambiente
from ambientes.AmbienteFarol import AmbienteFarol
from agentes.AgenteFarol import AgenteFarol
from ambientes.AmbienteRecolecao import AmbienteRecolecao
from politicas.PoliticaNoveltySearch import PoliticaNoveltySearch

class MotorDeSimulacao:

    def __init__(self, agentes: List[Agente], ambiente: Ambiente):
        self.agentes = agentes
        self.ambiente = ambiente
        self.passos = 0
        self.politica = None
        self.dados = {}

    def listaAgentes(self):
        return self.agentes

    def definePolitica(self, politica):
        if politica == "PoliticaNoveltySearch":
            self.politica = PoliticaNoveltySearch
        if politica == "PoliticaAleatoria":
            pass

    def cria(self, nome_do_ficheiro_parametros: str):
        try:
            with open(nome_do_ficheiro_parametros, 'r', encoding="utf-8") as file:
                self.dados = json.load(file)
                self.reset_ambiente()
        except Exception as e:
            print(f"Erro ao ler o ficheiro JSON: {e}", file=sys.stderr)
            return self
        return self

    def reset_ambiente(self):
        sizeX = self.dados.get('sizeX')
        sizeY = self.dados.get('sizeY')
        ambiente = self.dados.get('ambiente')
        lista_agentes = self.dados.get('agentes')
        obstaculos = self.dados.get('obstaculos')
        politica = self.dados.get('politica')
        self.definePolitica(politica)
        if ambiente == "Ambiente Farol":
            farol = self.dados.get('farol')
            self.ambiente = AmbienteFarol(sizeX, sizeY, (farol[0], farol[1]))
            tipo_agente = AgenteFarol
        if ambiente == "Ambiente Recolecao":
            self.ambiente = AmbienteRecolecao(sizeX, sizeY, [], [])
            ninhos = self.dados.get('ninhos')
            for pos in ninhos:
                self.ambiente.ninhos.append((pos[0], pos[1]))
            recursos = self.dados.get('recursos')
            for recurso in recursos:
                self.ambiente.recursos.append(recurso)
            tipo_agente = AgenteRecolecao
        self.passos = self.dados.get('passos')
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


    def executa(self):
        if self.politica == PoliticaNoveltySearch:
            print("Iniciando simulação com PoliticaNoveltySearch")
            self.executaEvolutivo()
        # if isinstance(self.politica, PoliticaAleatoria):
        #     print("Iniciando simulação com PoliticaAleatoria")
        #     pass
        else:
            print("Política desconhecida, não é possível executar a simulação")

    def executaEvolutivo(self):
        TAMANHO_POPULACAO = 160
        NUMERO_GERACOES = 50
        TAXA_MUTACAO = 0.01
        PESO_NOVIDADE = 4
        PESO_OBJETIVO = 1.0
        TAMANHO_TORNEIO = 5
        N_ARQUIVOS = 3

        arquivo_novidade = []
        self.politica.num_passos = self.passos
        populacao = [self.politica(num_passos=self.passos) for _ in range(TAMANHO_POPULACAO)]  # gera a população inicial com base nessa politica com movimentos aleatórios
        media_fitness_por_gen = []
        melhor_caminho_por_gen = []
        melhor_items_global = -1
        # melhor_caminho_global = []
        # melhor_fitness_global = -1.0

        print("INICIO EVOLUÇÃO")
        for gen in range(NUMERO_GERACOES):
            fitness_total = 0
            for individuo in populacao:
                individuo.reset()
                self.reset_ambiente()
                if len(self.agentes) > 0:
                    agente = self.agentes[0]
                    agente.setPolitica(individuo)
                    for _ in range(self.passos):
                        self.ambiente.observacaoPara(agente)
                        accao = agente.age()
                        self.ambiente.agir(accao, agente)
                        # self.ambiente.drawingWorld()
                        # self.ambiente.observacaoPara(agente)

                    # novelty
                    novelty = self.politica.computar_novelty(individuo.comportamento, arquivo_novidade, k=5)
                    individuo.novelty_score = novelty
                    # fitness
                    objetivo = individuo.calcular_fitness()
                    individuo.fitness_objetivo = (objetivo * PESO_OBJETIVO) + (novelty * PESO_NOVIDADE)
                    fitness_total += individuo.fitness_objetivo
            populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True)
            melhor_da_gen = populacao[0]
            media_fitness = fitness_total / TAMANHO_POPULACAO
            media_fitness_por_gen.append(media_fitness)
            melhor_caminho_por_gen.append(melhor_da_gen.caminho)
            print(f"Gen {gen + 1}: Média de fitness: {media_fitness:.2f} " f"(Itens: {melhor_da_gen.items_recolhidos}, Nov: {melhor_da_gen.novelty_score:.4f})")
            if melhor_da_gen.items_recolhidos > melhor_items_global:
                melhor_items_global = melhor_da_gen.items_recolhidos
                melhor_caminho_global = list(melhor_da_gen.caminho)
            populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True)
            for i in range(N_ARQUIVOS):
                arquivo_novidade.append(populacao[i].comportamento)
            populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True)
            nova_populacao = []
            nova_populacao.extend(populacao[:(TAMANHO_POPULACAO // 10)])
            while len(nova_populacao) < TAMANHO_POPULACAO:
                pai1 = self.politica.seleciona_pais(populacao, TAMANHO_TORNEIO)
                pai2 = self.politica.seleciona_pais(populacao, TAMANHO_TORNEIO)
                child1, child2 = PoliticaNoveltySearch.crossover(pai1, pai2)
                child1.mutar(TAXA_MUTACAO)
                child2.mutar(TAXA_MUTACAO)
                nova_populacao.append(child1)
                if len(nova_populacao) < TAMANHO_POPULACAO:
                    nova_populacao.append(child2)
            populacao = nova_populacao
        print("EVOLUÇÃO COMPLETA")

        plt.figure(figsize=(10, 5))
        plt.plot(media_fitness_por_gen, marker='o')
        plt.title("Média de Fitness por Geração")
        plt.xlabel("Geração")
        plt.ylabel("Fitness Médio")
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    sim = MotorDeSimulacao([], None).cria("simulador/mundoFarol.json")
    sim.executa()