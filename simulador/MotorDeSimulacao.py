import copy
import sys
import time
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
from politicas.PoliticaAleatoria import PoliticaAleatoria
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
            self.politica = PoliticaNoveltySearch()
        if politica == "PoliticaAleatoria":
            self.politica = PoliticaAleatoria()
        self.politica.objetivos = self.ambiente.objetivos
        self.politica.obstaculos = self.ambiente.obstaculos

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
        self.agentes = []
        sizeX = self.dados.get('sizeX')
        sizeY = self.dados.get('sizeY')
        ambiente = self.dados.get('ambiente')
        lista_agentes = self.dados.get('agentes')
        obstaculos = self.dados.get('obstaculos')
        self.passos = self.dados.get('passos')
        politica = self.dados.get('politica')
        if ambiente == "Ambiente Farol":
            farol = self.dados.get('farol')
            self.ambiente = AmbienteFarol(sizeX, sizeY, (farol[0], farol[1]))
            tipo_agente = AgenteFarol
        elif ambiente == "Ambiente Recolecao":
            ninhos_lista = []
            ninhos = self.dados.get('ninhos')
            for pos in ninhos:
                ninhos_lista.append((pos[0], pos[1]))
            recursos_originais = self.dados.get('recursos')
            recursos_copia = copy.deepcopy(recursos_originais)
            self.ambiente = AmbienteRecolecao(sizeX, sizeY, recursos_copia, ninhos_lista)
            tipo_agente = AgenteRecolecao
        if obstaculos:
            for pos in obstaculos:
                self.ambiente.obstaculos.append((pos[0], pos[1]))
        for ag in lista_agentes:
            nome_agente = ag['nome_agente']
            pos_ag = ag['pos_agente']
            agente = tipo_agente(nome_agente, pos_ag[0], pos_ag[1])
            agente.instala(SensorVisao())
            self.agentes.append(agente)
            self.ambiente.agentes.append(agente)
        politica = self.dados.get('politica')
        self.definePolitica(politica)



    def executa(self):
        print(self.politica)
        if isinstance(self.politica, PoliticaNoveltySearch):
            print("Iniciando simulação com PoliticaNoveltySearch")
            self.executaEvolutivo()
            return
        if isinstance(self.politica, PoliticaAleatoria):
            print("Iniciando simulação com PoliticaAleatoria")
            self.executaAleatorio()
            return
        else:
            print("Política desconhecida, não é possível executar a simulação")
            return

    def executaAleatorio(self):
        NUMERO_EXERCUCOES = 3
        numero_passos_por_ex = []
        print("INÍCIO DA SIMULAÇÃO")
        for _ in range(NUMERO_EXERCUCOES):
            self.reset_ambiente()
            passos = 0
            if self.agentes:
                for ag in self.agentes:
                    ag.setPolitica(self.politica)
                    for _ in range(self.passos):
                        if self.politica.acabou:
                            break
                        self.ambiente.observacaoPara(ag)
                        accao = ag.age()
                        self.ambiente.agir(accao, ag)
                        passos += 1
                        # print(passos)
                        # self.ambiente.drawingWorld()
                        # time.sleep(1)
            numero_passos_por_ex.append(self.politica.passo_atual)
        media_passos = sum(numero_passos_por_ex) / len(numero_passos_por_ex)
        print(f"FIM DA SIMULAÇÃO.")

        print(f"Média de Passos: {media_passos:.2f}")
        plt.figure(figsize=(10, 6))
        plt.plot(numero_passos_por_ex, marker='o', linestyle='-', color='blue', alpha=0.6, label='Passos por Tentativa')
        plt.axhline(y=media_passos, color='red', linestyle='--', linewidth=2, label=f'Média ({media_passos:.1f})')
        plt.title("Desempenho da Política Aleatória/Heurística")
        plt.xlabel("Número da Execução (1-100)")
        plt.ylabel("Número de Passos Gastos")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()


    def executaEvolutivo(self):
        TAMANHO_POPULACAO = 160
        NUMERO_GERACOES = 50
        TAXA_MUTACAO = 0.01
        PESO_NOVIDADE = 4
        PESO_OBJETIVO = 1.0
        TAMANHO_TORNEIO = 5
        N_ARQUIVOS = 3

        arquivo_novidade = []
        classe = type(self.politica)
        self.politica.num_passos = self.passos
        populacao = [classe(num_passos=self.passos) for _ in range(TAMANHO_POPULACAO)]  # gera a população inicial com base nessa politica com movimentos aleatórios
        media_fitness_por_gen = []
        melhor_caminho_por_gen = []
        melhor_items_global = -1
        melhor_passos_por_gen = 0
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
                    # passos = 0
                    for _ in range(self.passos):
                        if individuo.acabou:
                            break
                        self.ambiente.observacaoPara(agente)
                        accao = agente.age()
                        self.ambiente.agir(accao, agente)
                        # passos += 1
                        # print(passos)
                        # self.ambiente.drawingWorld()
                        # time.sleep(1.0)
                    # novelty
                    novelty = self.politica.computar_novelty(individuo.comportamento, arquivo_novidade, k = 5)
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
            print(f"Gen {gen + 1}: Média de fitness: {media_fitness:.2f} " f"(Itens: {melhor_da_gen.items_recolhidos}, Nov: {melhor_da_gen.novelty_score:.4f}) " f"Passos: {melhor_da_gen.passo_atual}")
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
    sim = MotorDeSimulacao([], None).cria("simulador/mundoRecolecao.json")
    sim.executa()