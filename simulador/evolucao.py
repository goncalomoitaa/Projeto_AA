import copy
import random
from simulador.MotorDeSimulacao import MotorDeSimulacao

# --- parâmetros do GA ---
TAMANHO_POP = 10
GERACOES = 20
TAXA_MUTACAO = 0.3

# limites dos genes (podes ajustar)
LIM_PESO_OBJETIVO = (0.0, 1.0)
LIM_PROB_RANDOM   = (0.0, 0.3)


def gen_random_genotipo():
    return {
        "peso_objetivo": random.uniform(*LIM_PESO_OBJETIVO),
        "prob_random":   random.uniform(*LIM_PROB_RANDOM),
    }


def mutar(genotipo):
    g = copy.deepcopy(genotipo)
    if random.random() < 0.5:
        g["peso_objetivo"] = min(
            LIM_PESO_OBJETIVO[1],
            max(LIM_PESO_OBJETIVO[0],
                g["peso_objetivo"] + random.uniform(-0.2, 0.2))
        )
    else:
        g["prob_random"] = min(
            LIM_PROB_RANDOM[1],
            max(LIM_PROB_RANDOM[0],
                g["prob_random"] + random.uniform(-0.05, 0.05))
        )
    return g


def crossover(pai, mae):
    filho = {}
    for k in pai.keys():
        filho[k] = random.choice([pai[k], mae[k]])
    return filho


def avaliar_genotipo(genotipo, ficheiro_mundo, nome_politica):
    """
    Cria uma simulação com a política indicada e aplica o genótipo aos agentes.
    O fitness é o nº total de posições distintas visitadas (novelty).
    """
    sim = MotorDeSimulacao([], None).cria(ficheiro_mundo)

    # aqui assumimos que o ficheiro JSON já tem "politica": nome_politica
    # se quiseres ignorar o que está no JSON, podes forçar a política com:
    #   for agente in sim.listaAgentes(): agente.setPolitica(PoliticaXxx())

    for agente in sim.listaAgentes():
        agente.genotipo = copy.deepcopy(genotipo)

    visitas = sim.executa()  # dict nome -> set(posicoes)

    fitness = sum(len(posicoes) for posicoes in visitas.values())
    return fitness


def evoluir(ficheiro_mundo, nome_politica):
    # população inicial
    populacao = [gen_random_genotipo() for _ in range(TAMANHO_POP)]

    for gen in range(GERACOES):
        avaliacoes = []
        for g in populacao:
            f = avaliar_genotipo(g, ficheiro_mundo, nome_politica)
            avaliacoes.append((f, g))

        avaliacoes.sort(key=lambda x: x[0], reverse=True)
        melhor_f, melhor_g = avaliacoes[0]
        print(f"Geração {gen}: melhor_fitness={melhor_f:.2f}, melhor_genotipo={melhor_g}")

        # elitismo: mantemos o top 2
        nova_pop = [avaliacoes[0][1], avaliacoes[1][1]]

        # resto por crossover + mutação
        while len(nova_pop) < TAMANHO_POP:
            pai = random.choice(avaliacoes[:5])[1]
            mae = random.choice(avaliacoes[:5])[1]
            filho = crossover(pai, mae)

            if random.random() < TAXA_MUTACAO:
                filho = mutar(filho)

            nova_pop.append(filho)

        populacao = nova_pop

    # no fim, reavalia o melhor
    avaliacoes_finais = [(avaliar_genotipo(g, ficheiro_mundo, nome_politica), g)
                         for g in populacao]
    avaliacoes_finais.sort(key=lambda x: x[0], reverse=True)
    best_f, best_g = avaliacoes_finais[0]
    print("\n=== RESULTADO FINAL ===")
    print("Melhor fitness:", best_f)
    print("Melhor genótipo:", best_g)
    return best_f, best_g


if __name__ == "__main__":
    # ESCOLHES AQUI A POLÍTICA E O MUNDO
    ficheiro = "mundoRecolecao.json"   # ou "mundoFarol.json"
    politica = "PoliticaNoveltySearch"  # ou "PoliticaAleatoria", etc.

    evoluir(ficheiro, politica)
