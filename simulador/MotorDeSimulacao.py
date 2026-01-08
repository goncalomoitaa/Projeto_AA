import copy
import sys
import time
from typing import List
import json
from matplotlib import pyplot as plt

# Importação dos módulos do seu projeto
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

    def definePolitica(self, nome_politica):
        if nome_politica == "PoliticaNoveltySearch":
            self.politica = PoliticaNoveltySearch()
        elif nome_politica == "PoliticaAleatoria":
            self.politica = PoliticaAleatoria()
            if isinstance(self.ambiente, AmbienteRecolecao):
                self.politica.ninhos = self.dados.get('ninhos')
        elif nome_politica == "PoliticaQLearning":
            self.politica = PoliticaQLearning()

        self.politica.objetivos = self.ambiente.objetivos
        self.politica.obstaculos = self.ambiente.obstaculos

    def executa(self):
        if isinstance(self.politica, PoliticaNoveltySearch):
            return self.executaEvolutivo()
        if isinstance(self.politica, PoliticaAleatoria):
            return self.executaAleatorio()
        if isinstance(self.politica, PoliticaQLearning):
            return self.executaAprendizagemReforco()
        return None

    def cria(self, nome_do_ficheiro_parametros: str):
        try:
            with open(nome_do_ficheiro_parametros, 'r', encoding="utf-8") as file:
                self.dados = json.load(file)
                self.reset_ambiente()
        except Exception as e:
            print(f"Erro ao ler o ficheiro JSON: {e}", file=sys.stderr)
        return self

    def reset_ambiente(self):
        self.agentes = []
        sizeX = self.dados.get('sizeX')
        sizeY = self.dados.get('sizeY')
        ambiente_str = self.dados.get('ambiente')
        lista_agentes = self.dados.get('agentes')
        obstaculos = self.dados.get('obstaculos')
        self.passos = self.dados.get('passos')

        if ambiente_str == "Ambiente Farol":
            farol = self.dados.get('farol')
            self.ambiente = AmbienteFarol(sizeX, sizeY, (farol[0], farol[1]))
            tipo_agente = AgenteFarol
        elif ambiente_str == "Ambiente Recolecao":
            ninhos = [(pos[0], pos[1]) for pos in self.dados.get('ninhos')]
            recursos_copia = copy.deepcopy(self.dados.get('recursos'))
            self.ambiente = AmbienteRecolecao(sizeX, sizeY, recursos_copia, ninhos)
            tipo_agente = AgenteRecolecao

        if obstaculos:
            self.ambiente.obstaculos = [(pos[0], pos[1]) for pos in obstaculos]

        for ag in lista_agentes:
            agente = tipo_agente(ag['nome_agente'], ag['pos_agente'][0], ag['pos_agente'][1])
            agente.instala(SensorVisao())
            self.agentes.append(agente)
            self.ambiente.agentes.append(agente)

    def executaAleatorio(self):
        historico_passos, historico_colisoes, historico_recompensas, sucessos = [], [], [], 0
        for _ in range(self.NUMERO_EXECUCOES):
            self.reset_ambiente()
            self.politica.passo_atual = 0
            self.politica.objetivo = 0  # Reset da recompensa acumulada
            self.politica.acabou = False
            agente = self.agentes[0]
            agente.setPolitica(self.politica)
            agente.colisoes = 0

            for _ in range(self.passos):
                if self.politica.acabou: break
                self.ambiente.observacaoPara(agente)
                self.ambiente.agir(agente.age(), agente)

            if self.politica.acabou: sucessos += 1
            historico_passos.append(self.politica.passo_atual)
            historico_colisoes.append(getattr(agente, 'colisoes', 0))
            historico_recompensas.append(getattr(self.politica, 'objetivo', 0))

        return {"passos": historico_passos, "colisoes": historico_colisoes,
                "recompensa": historico_recompensas, "sucesso": (sucessos / self.NUMERO_EXECUCOES) * 100}

    def executaEvolutivo(self):
        TAMANHO_POPULACAO = 160
        historico_passos, historico_colisoes, historico_recompensas, sucessos = [], [], [], 0
        arquivo_novidade = []
        classe = type(self.politica)
        populacao = [classe(num_passos=self.passos) for _ in range(TAMANHO_POPULACAO)]

        for gen in range(self.NUMERO_EXECUCOES):
            for individuo in populacao:
                individuo.reset()
                self.reset_ambiente()
                agente = self.agentes[0]
                agente.setPolitica(individuo)
                agente.colisoes = 0
                for _ in range(self.passos):
                    if individuo.acabou: break
                    self.ambiente.observacaoPara(agente)
                    self.ambiente.agir(agente.age(), agente)

                individuo.colisoes = agente.colisoes
                novelty = self.politica.computar_novelty(individuo.comportamento, arquivo_novidade, k=5)
                individuo.novelty_score = novelty
                individuo.fitness_objetivo = (individuo.calcular_fitness() * 1.0) + (novelty * 4)

            populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True)
            melhor = populacao[0]
            if melhor.acabou: sucessos += 1
            historico_passos.append(melhor.passo_atual)
            historico_colisoes.append(melhor.colisoes)
            historico_recompensas.append(melhor.objetivo)

            arquivo_novidade.extend([p.comportamento for p in populacao[:3]])
            nova_populacao = populacao[:TAMANHO_POPULACAO // 10]
            while len(nova_populacao) < TAMANHO_POPULACAO:
                p1, p2 = self.politica.seleciona_pais(populacao, 5), self.politica.seleciona_pais(populacao, 5)
                child1, child2 = PoliticaNoveltySearch.crossover(p1, p2)
                child1.mutar(0.01)
                child2.mutar(0.01)
                nova_populacao.extend([child1, child2])
            populacao = nova_populacao[:TAMANHO_POPULACAO]

        return {"passos": historico_passos, "colisoes": historico_colisoes,
                "recompensa": historico_recompensas, "sucesso": (sucessos / self.NUMERO_EXECUCOES) * 100}

    def executaAprendizagemReforco(self):
        politica_global = PoliticaQLearning()
        historico_passos, historico_colisoes, historico_recompensas, sucessos = [], [], [], 0
        for episodio in range(self.NUMERO_EXECUCOES):
            self.reset_ambiente()
            agente = self.agentes[0]
            agente.setPolitica(politica_global)
            agente.colisoes = 0
            politica_global.passo_atual = 0
            politica_global.objetivo = 0  # Reset da recompensa acumulada
            politica_global.acabou = False

            for _ in range(self.passos):
                self.ambiente.observacaoPara(agente)
                self.ambiente.agir(agente.age(), agente)
                if getattr(politica_global, "acabou", False): break

            if getattr(politica_global, "acabou", False): sucessos += 1
            historico_passos.append(politica_global.passo_atual)
            historico_colisoes.append(agente.colisoes)
            historico_recompensas.append(politica_global.objetivo)
            politica_global.fim_episodio()

        return {"passos": historico_passos, "colisoes": historico_colisoes,
                "recompensa": historico_recompensas, "sucesso": (sucessos / self.NUMERO_EXECUCOES) * 100}

    def gerar_graficos_comparativos(self, resultados):
        cores = {"PoliticaAleatoria": "blue", "PoliticaNoveltySearch": "green", "PoliticaQLearning": "red"}

        # 1. Gráfico de Passos
        plt.figure("Passos por Tentativa", figsize=(10, 6))
        for nome, data in resultados.items():
            plt.plot(data["passos"], label=nome, color=cores.get(nome, "black"))
        plt.title("Métrica: Passos por Episódio (Eficiência)")
        plt.xlabel("Execução/Geração")
        plt.ylabel("Passos")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 2. Gráfico de Colisões
        plt.figure("Colisões por Tentativa", figsize=(10, 6))
        for nome, data in resultados.items():
            plt.plot(data["colisoes"], label=nome, color=cores.get(nome, "black"))
        plt.title("Métrica: Colisões (Quantidade)")
        plt.xlabel("Execução/Geração")
        plt.ylabel("Colisões")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 3. Gráfico de Recompensa Acumulada (NOVO)
        plt.figure("Recompensa Acumulada", figsize=(10, 6))
        for nome, data in resultados.items():
            plt.plot(data["recompensa"], label=nome, color=cores.get(nome, "black"))
        plt.title("Métrica: Recompensa Acumulada por Episódio")
        plt.xlabel("Execução/Geração")
        plt.ylabel("Score Total")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 4. Gráfico de Taxa de Sucesso
        plt.figure("Taxa de Sucesso", figsize=(8, 6))
        nomes = list(resultados.keys())
        taxas = [resultados[n]["sucesso"] for n in nomes]
        plt.bar(nomes, taxas, color=[cores.get(n) for n in nomes])
        plt.title("Métrica: Taxa de Sucesso (%)")
        plt.ylim(0, 110)
        for i, v in enumerate(taxas):
            plt.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold')
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        plt.show()


if __name__ == "__main__":
    motor = MotorDeSimulacao([], None).cria("mundoFarol.json")
    lista_politicas = ["PoliticaAleatoria", "PoliticaNoveltySearch", "PoliticaQLearning"]
    resultados_finais = {}

    for p_nome in lista_politicas:
        print(f"A executar: {p_nome}...")
        motor.definePolitica(p_nome)
        resultados_finais[p_nome] = motor.executa()

    motor.gerar_graficos_comparativos(resultados_finais)