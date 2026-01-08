import copy
import sys
import math
import json
from typing import List
from matplotlib import pyplot as plt

# Importação dos módulos do projeto
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
            self.politica = PoliticaNoveltySearch(num_passos=self.passos)
        elif nome_politica == "PoliticaAleatoria":
            self.politica = PoliticaAleatoria()
            if self.dados.get('ambiente') == "Ambiente Recolecao":
                self.politica.ninhos = self.dados.get('ninhos', [])
        elif nome_politica == "PoliticaQLearning":
            self.politica = PoliticaQLearning()

        self.politica.objetivos = getattr(self.ambiente, 'objetivos', [])
        self.politica.obstaculos = getattr(self.ambiente, 'obstaculos', [])

    def reset_ambiente(self):
        self.agentes = []
        sizeX, sizeY = self.dados.get('sizeX'), self.dados.get('sizeY')
        ambiente_str = self.dados.get('ambiente')
        self.passos = self.dados.get('passos')

        if ambiente_str == "Ambiente Farol":
            self.ambiente = AmbienteFarol(sizeX, sizeY, self.dados.get('farol'))
            tipo_agente = AgenteFarol
        elif ambiente_str == "Ambiente Recolecao":
            ninhos = [(pos[0], pos[1]) for pos in self.dados.get('ninhos')]
            recursos = copy.deepcopy(self.dados.get('recursos'))
            self.ambiente = AmbienteRecolecao(sizeX, sizeY, recursos, ninhos)
            tipo_agente = AgenteRecolecao

        if self.dados.get('obstaculos'):
            self.ambiente.obstaculos = [(pos[0], pos[1]) for pos in self.dados.get('obstaculos')]

        for ag_info in self.dados.get('agentes'):
            agente = tipo_agente(ag_info['nome_agente'], ag_info['pos_agente'][0], ag_info['pos_agente'][1])
            agente.instala(SensorVisao())
            self.agentes.append(agente)
            self.ambiente.agentes.append(agente)

    def calcular_distancia_manhattan(self, agente):
        if hasattr(self.ambiente, 'farol'):
            fx, fy = self.ambiente.farol
            return abs(agente.x - fx) + abs(agente.y - fy)
        return 0

    def executar_episodio(self, pol_instancia):
        self.reset_ambiente()
        agente = self.agentes[0]
        agente.setPolitica(pol_instancia)

        pol_instancia.passo_atual = 0
        pol_instancia.objetivo = 0
        pol_instancia.acabou = False
        agente.colisoes = 0

        recursos_recolhidos_total = 0
        recursos_depositados_total = 0

        for _ in range(self.passos):
            if pol_instancia.acabou: break

            mochila_antes = getattr(agente, 'mochila', 0)
            self.ambiente.observacaoPara(agente)
            self.ambiente.agir(agente.age(), agente)
            mochila_depois = getattr(agente, 'mochila', 0)

            if self.dados.get('ambiente') == "Ambiente Recolecao":
                if mochila_depois > mochila_antes:
                    recursos_recolhidos_total += (mochila_depois - mochila_antes)
                elif mochila_depois < mochila_antes:
                    recursos_depositados_total += (mochila_antes - mochila_depois)

        if self.dados.get('ambiente') == "Ambiente Recolecao":
            sucesso = 1 if (len(self.ambiente.recursos) == 0 and agente.mochila == 0) else 0
        else:
            sucesso = 1 if pol_instancia.acabou else 0

        return {
            "passos": pol_instancia.passo_atual,
            "recompensa": pol_instancia.objetivo,
            "sucesso": sucesso,
            "colisoes": agente.colisoes,
            "distancia": self.calcular_distancia_manhattan(agente),
            "recolhidos": recursos_recolhidos_total,
            "depositados": recursos_depositados_total,
            "valor_total": getattr(self.ambiente, 'pontos', 0)
        }

    def avaliar_politica(self, nome_pol):
        hist = {k: [] for k in ["passos", "recompensa", "sucesso", "colisoes", "distancia", "recolhidos", "depositados",
                                "valor_total"]}

        if nome_pol == "PoliticaNoveltySearch":
            arquivo_novidade = []
            populacao = [PoliticaNoveltySearch(num_passos=self.passos) for _ in range(160)]
            for gen in range(self.NUMERO_EXECUCOES):
                for ind in populacao:
                    ind.reset()
                    self.executar_episodio(ind)
                    ind.fitness_objetivo = ind.calcular_fitness() + (
                                ind.computar_novelty(ind.comportamento, arquivo_novidade, 5) * 4)

                populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True)
                melhor = populacao[0]
                ep = self.executar_episodio(melhor)
                for k, v in zip(hist.keys(), ep.values()): hist[k].append(v)

                arquivo_novidade.extend([p.comportamento for p in populacao[:3]])
                nova = [copy.deepcopy(p) for p in populacao[:16]]
                while len(nova) < 160:
                    p1, p2 = PoliticaNoveltySearch.seleciona_pais(populacao, 5), PoliticaNoveltySearch.seleciona_pais(
                        populacao, 5)
                    c1, c2 = PoliticaNoveltySearch.crossover(p1, p2)
                    c1.mutar(0.01);
                    c2.mutar(0.01);
                    nova.extend([c1, c2])
                populacao = nova[:160]
        else:
            self.definePolitica(nome_pol)
            for _ in range(self.NUMERO_EXECUCOES):
                ep = self.executar_episodio(self.politica)
                for k, v in zip(hist.keys(), ep.values()): hist[k].append(v)
                if hasattr(self.politica, 'fim_episodio'): self.politica.fim_episodio()

        return hist

    def gerar_relatorio_visual(self, resultados_globais):
        cores = {"PoliticaAleatoria": "blue", "PoliticaNoveltySearch": "green", "PoliticaQLearning": "red"}
        grid_conf = {"linestyle": '--', "alpha": 0.3}

        plt.figure("Métrica: Número de Passos", figsize=(8, 5))
        for n, d in resultados_globais.items(): plt.plot(d["passos"], label=n, color=cores[n])
        plt.title("Evolução: Passos por Episódio");
        plt.ylabel("Passos");
        plt.legend();
        plt.grid(True, **grid_conf)

        plt.figure("Métrica: Recompensa Acumulada", figsize=(8, 5))
        for n, d in resultados_globais.items(): plt.plot(d["recompensa"], label=n, color=cores[n])
        plt.title("Evolução: Recompensa Acumulada");
        plt.ylabel("Score");
        plt.legend();
        plt.grid(True, **grid_conf)

        plt.figure("Métrica: Taxa de Sucesso", figsize=(7, 5))
        nomes = list(resultados_globais.keys())
        taxas = [(sum(resultados_globais[n]["sucesso"]) / self.NUMERO_EXECUCOES) * 100 for n in nomes]
        plt.bar(nomes, taxas, color=[cores[n] for n in nomes], edgecolor='black')
        plt.title("Eficácia: Taxa de Sucesso (%)");
        plt.ylim(0, 115)
        for i, v in enumerate(taxas): plt.text(i, v + 2, f"{int(v)}%", ha='center', fontweight='bold')
        plt.grid(True, axis='y', **grid_conf)

        plt.figure("Métrica: Colisões", figsize=(8, 5))
        for n, d in resultados_globais.items(): plt.plot(d["colisoes"], label=n, color=cores[n])
        plt.title("Evolução: Número de Colisões");
        plt.ylabel("Colisões");
        plt.legend();
        plt.grid(True, **grid_conf)

        if self.dados.get('ambiente') == "Ambiente Recolecao":
            plt.figure("Métrica: Recursos Recolhidos", figsize=(8, 5))
            for n, d in resultados_globais.items(): plt.plot(d["recolhidos"], label=n, color=cores[n])
            plt.title("Foraging: Recursos Recolhidos");
            plt.ylabel("Quantidade");
            plt.legend();
            plt.grid(True, **grid_conf)

            plt.figure("Métrica: Recursos Depositados", figsize=(8, 5))
            for n, d in resultados_globais.items(): plt.plot(d["depositados"], label=n, color=cores[n])
            plt.title("Foraging: Recursos Depositados");
            plt.ylabel("Quantidade");
            plt.legend();
            plt.grid(True, **grid_conf)

            plt.figure("Métrica: Valor Total Depositado", figsize=(8, 5))
            for n, d in resultados_globais.items(): plt.plot(d["valor_total"], label=n, color=cores[n])
            plt.title("Foraging: Valor Total Depositado");
            plt.ylabel("Soma de Valores");
            plt.legend();
            plt.grid(True, **grid_conf)

            plt.figure("Métrica: Eficiência Foraging", figsize=(8, 5))
            for n, d in resultados_globais.items():
                efic = [v / p if p > 0 else 0 for v, p in zip(d["valor_total"], d["passos"])]
                plt.plot(efic, label=n, color=cores[n])
            plt.title("Foraging: Eficiência (Valor/Passo)");
            plt.ylabel("Rácio");
            plt.legend();
            plt.grid(True, **grid_conf)

        if self.dados.get('ambiente') == "Ambiente Farol":
            plt.figure("Métrica: Distância ao Farol", figsize=(8, 5))
            for n, d in resultados_globais.items(): plt.plot(d["distancia"], label=n, color=cores[n])
            plt.title("Navegação: Distância Final ao Alvo");
            plt.ylabel("Distância");
            plt.legend();
            plt.grid(True, **grid_conf)

        plt.show()

    def cria(self, nome_do_ficheiro_parametros: str):
        try:
            with open(nome_do_ficheiro_parametros, 'r', encoding="utf-8") as file:
                self.dados = json.load(file)
                self.reset_ambiente()
        except Exception:
            pass
        return self


if __name__ == "__main__":
    motor = MotorDeSimulacao([], None).cria("mundoRecolecao.json")
    politicas = ["PoliticaAleatoria", "PoliticaNoveltySearch", "PoliticaQLearning"]
    res_finais = {p: motor.avaliar_politica(p) for p in politicas}
    motor.gerar_relatorio_visual(res_finais)