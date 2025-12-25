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
from politicas.PoliticaQLearning import PoliticaQLearning

class MotorDeSimulacao:

    def __init__(self, agentes: List[Agente], ambiente: Ambiente):
        self.agentes = agentes
        self.ambiente = ambiente
        self.dados = {}
        self.politica = None
        self.passos = 0
        self.NUMERO_EXECUCOES = 50

    def listaAgentes(self):
        return self.agentes

    def definePolitica(self, politica):
        if politica == "PoliticaNoveltySearch":
            self.politica = PoliticaNoveltySearch()
        if politica == "PoliticaAleatoria":
            self.politica = PoliticaAleatoria()
            if isinstance(self.ambiente, AmbienteRecolecao):
                self.politica.ninhos = self.dados.get('ninhos')
        if politica == "PoliticaQLearning":
            self.politica = PoliticaQLearning()
        self.politica.objetivos = self.ambiente.objetivos
        self.politica.obstaculos = self.ambiente.obstaculos

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
        if isinstance(self.politica, PoliticaQLearning):
            print("Iniciando simulação com PoliticaQLearning")
            self.executaAprendizagemReforco()
            return
        else:
            print("Política desconhecida, não é possível executar a simulação")
            return

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

    def executaAleatorio(self):
        historico_passos = []
        sucessos = 0
        print("INÍCIO DA SIMULAÇÃO")
        for _ in range(self.NUMERO_EXECUCOES):
            self.reset_ambiente()
            if self.agentes:
                for _ in range(self.passos):
                    for ag in self.agentes:
                        if self.politica.acabou:
                            self.ambiente.drawingWorld()
                            time.sleep(1)
                            sucessos += 1
                            break
                        self.ambiente.observacaoPara(ag)
                        accao = ag.age()
                        self.ambiente.agir(accao, ag)
                        self.ambiente.drawingWorld()
                        time.sleep(1)
                        ag.setPolitica(self.politica)
            historico_passos.append(self.politica.passo_atual)
        media_passos = sum(historico_passos) / len(historico_passos)
        taxa_sucesso = (sucessos / self.NUMERO_EXECUCOES) * 100
        print(f"FIM DA SIMULAÇÃO.")
        print(f"Média de Passos: {media_passos:.2f}")
        print(f"Taxa de sucesso: {taxa_sucesso:.2f}%")
        plt.figure(figsize=(10, 6))
        plt.plot(historico_passos, marker='o', linestyle='-', color='blue', alpha=0.6, label='Passos por Tentativa')
        plt.axhline(y=media_passos, color='red', linestyle='--', linewidth=2, label=f'Média ({media_passos:.1f})')
        plt.title("Desempenho da Política Aleatória/Heurística")
        plt.xlabel(f"Número da Execução (1-{self.NUMERO_EXECUCOES})")
        plt.ylabel("Número de Passos Gastos")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def executaEvolutivo(self):
        TAMANHO_POPULACAO = 160
        NUMERO_GERACOES = self.NUMERO_EXECUCOES
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
        melhor_caminho_global = []
        melhor_fitness_global = -1.0
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
                        if individuo.acabou:
                            break
                        self.ambiente.observacaoPara(agente)
                        accao = agente.age()
                        self.ambiente.agir(accao, agente)
                        # self.ambiente.drawingWorld()
                        # time.sleep(1.0)
                    # novelty
                    novelty = self.politica.computar_novelty(individuo.comportamento, arquivo_novidade, k = 5)
                    individuo.novelty_score = novelty
                    # fitness
                    objetivo = individuo.calcular_fitness()
                    individuo.fitness_objetivo = (objetivo * PESO_OBJETIVO) + (novelty * PESO_NOVIDADE)
                    fitness_total += individuo.fitness_objetivo
            populacao.sort(key = lambda x : x.fitness_objetivo, reverse = True)
            melhor_da_gen = populacao[0]
            if melhor_da_gen.items_recolhidos > melhor_items_global:
                melhor_fitness_global = melhor_da_gen.fitness_objetivo
                melhor_caminho_global = copy.deepcopy(melhor_da_gen)
            media_fitness = fitness_total / TAMANHO_POPULACAO
            media_fitness_por_gen.append(media_fitness)
            melhor_caminho_por_gen.append(melhor_da_gen.caminho)
            print(f"Gen {gen + 1}: Média de fitness: {media_fitness:.2f} " f"(Itens_melhor_da_gen: {melhor_da_gen.items_recolhidos}, Nov_melhor_da_gen: {melhor_da_gen.novelty_score:.4f}) " f"Passos_melhor_da_gen: {melhor_da_gen.passo_atual}")
            populacao.sort(key = lambda x : x.fitness_objetivo, reverse = True)
            for i in range(N_ARQUIVOS):
                arquivo_novidade.append(populacao[i].comportamento)
            populacao.sort(key = lambda x : x.fitness_objetivo, reverse = True)
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
        if melhor_caminho_global:
            print(f"\n>>> A MOSTRAR REPLAY DO CAMPEÃO (Fitness: {melhor_fitness_global:.2f}) <<<")
            self.reset_ambiente()
            agente_final = self.agentes[0]
            agente_final.setPolitica(melhor_caminho_global)
            melhor_caminho_global.acabou = False
            melhor_caminho_global.passo_atual = 0
            melhor_caminho_global.items_recolhidos = 0
            if hasattr(melhor_caminho_global, 'tem_carga'): melhor_caminho_global.tem_carga = False
            for _ in range(self.passos):
                if melhor_caminho_global.acabou:
                    break
                self.ambiente.observacaoPara(agente_final)
                accao = agente_final.age()
                self.ambiente.agir(accao, agente_final)
                self.ambiente.drawingWorld()
                time.sleep(0.5)
        plt.figure(figsize=(10, 5))
        plt.plot(media_fitness_por_gen, marker='o')
        plt.title("Média de Fitness por Geração")
        plt.xlabel("Geração")
        plt.ylabel("Fitness Médio")
        plt.grid(True)
        plt.show()

    def executaAprendizagemReforco(self):
        LOG_FREQ = 1
        politica_global = PoliticaQLearning()
        historico_passos = []
        historico_items = []
        print("INÍCIO DA SIMULAÇÃO")
        for episodio in range(self.NUMERO_EXECUCOES):
            self.reset_ambiente()
            if not self.agentes:
                break
            agente = self.agentes[0]
            agente.setPolitica(politica_global)
            passos_realizados = 0
            for passo in range(self.passos):
                self.ambiente.observacaoPara(agente)
                accao = agente.age()
                self.ambiente.agir(accao, agente)
                passos_realizados += 1
                if hasattr(politica_global, "acabou") and politica_global.acabou:
                    break
            items_total = politica_global.items_recolhidos
            historico_passos.append(passos_realizados)
            historico_items.append(items_total)
            if episodio % LOG_FREQ == 0:
                print(f"Episódio {episodio} | Epsilon: {politica_global.epsilon:.3f} | "
                      f"Passos: {passos_realizados} | Items (Apanhar+Depositar): {items_total}")
            politica_global.fim_episodio()
        print(f"FIM DA SIMULAÇÃO.")
        print(f"Média Final de Passos: {sum(historico_passos[-10:]) / 10:.2f}")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(historico_passos, color='blue', alpha=0.6, label='Passos')
        ax1.set_title("Eficiência (Passos para Concluir)")
        ax1.set_ylabel("Passos")
        ax1.grid(True, alpha=0.3)
        ax2.plot(historico_items, color='green', alpha=0.6, label='Items (Ações de Sucesso)')
        ax2.set_title("Eficácia (Soma de Recolhas e Depósitos)")
        ax2.set_xlabel("Episódios")
        ax2.set_ylabel("Total Ações")
        ax2.set_ylim(0, 5)
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    sim = MotorDeSimulacao([], None).cria("mundoRecolecao.json")
    sim.executa()