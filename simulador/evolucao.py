import random

from matplotlib import pyplot as plt
from politicas.PoliticaNoveltySearch import PoliticaNoveltySearch
from simulador.MotorDeSimulacao import MotorDeSimulacao


def distancia_jaccard(set1, set2): #mede o quão diferente são os dois caminhos
    intersecao = len(set1 & set2)
    uniao = len(set1 | set2)
    return 1 - (intersecao / uniao) if uniao != 0 else 0

def computar_novelty(comportamento_corrente, arquivo, k = 5): #calcula a novidade para os k vizinhos mais próximos
    if not arquivo:
        return 1.0 #Todo 1.0 ou 0.0?
    distancias = [distancia_jaccard(comportamento_corrente, b) for b in arquivo]#compara o caminho feito pelo o agente com o da memória passada
    distancias.sort()
    if len(distancias) >= k:
        return sum(distancias[:k]) / k
    else:
        return sum(distancias) / len(distancias)

def seleciona_pais(populcao, tamanho_torneio):
    torneio = random.sample(populcao, tamanho_torneio)
    torneio.sort(key=lambda x: x.fitness_objetivo, reverse=True)
    return torneio[0]

def evoluir():
    TAMANHO_POPULACAO = 160
    NUMERO_GERACOES = 50
    TAXA_MUTACAO = 0.01
    NUM_PASSOS = 45
    PESO_NOVIDADE = 4
    PESO_OBJETIVO = 1.0
    TAMANHO_TORNEIO = 5
    N_ARQUIVOS = 3

    arquivo_novidade = []
    populacao = [PoliticaNoveltySearch(num_passos=NUM_PASSOS) for _ in range(TAMANHO_POPULACAO)] #gera a população inicial com base nessa politica com movimentos aleatórios
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
            motor = MotorDeSimulacao([], None).cria("mundoRecolecao.json")
            if len(motor.agentes) > 0:
                motor.agentes[0].setPolitica(individuo)
            motor.executa()
            #novelty
            novelty = computar_novelty(individuo.comportamento, arquivo_novidade)
            individuo.novelty_score = novelty
            #fitness
            objetivo = individuo.calcular_fitness()
            individuo.fitness_objetivo = (objetivo * PESO_OBJETIVO) + (novelty * PESO_NOVIDADE)
            fitness_total += individuo.fitness_objetivo
        populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True)
        melhor_da_gen = populacao[0]
        media_fitness = fitness_total / TAMANHO_POPULACAO
        media_fitness_por_gen.append(media_fitness)
        melhor_caminho_por_gen.append(melhor_da_gen.caminho)
        # best_nov = computar_novelty(melhor_da_gen.comportamento, arquivo_novidade)
        # best_obj = melhor_da_gen.calcular_fitness()
        # avg_items = sum(ind.items_recolhidos for ind in populacao) / TAMANHO_POPULACAO
        # passos = len(melhor_da_gen.caminho)
        print(f"Gen {gen + 1}: Média de fitness: {media_fitness:.2f} " f"(Itens: {melhor_da_gen.items_recolhidos}, Nov: {melhor_da_gen.novelty_score:.4f})")
        if melhor_da_gen.items_recolhidos > melhor_items_global:
            melhor_items_global = melhor_da_gen.items_recolhidos
            melhor_caminho_global = list(melhor_da_gen.caminho)
        populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True) #Todo ????
        for i in range(N_ARQUIVOS):
            arquivo_novidade.append(populacao[i].comportamento)
        populacao.sort(key=lambda x: x.fitness_objetivo, reverse=True)
        nova_populacao = []
        nova_populacao.extend(populacao[:(TAMANHO_POPULACAO // 10)])
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1 = seleciona_pais(populacao, TAMANHO_TORNEIO)
            pai2 = seleciona_pais(populacao, TAMANHO_TORNEIO)
            child1, child2 = PoliticaNoveltySearch.crossover(pai1, pai2)
            child1.mutar(TAXA_MUTACAO)
            child2.mutar(TAXA_MUTACAO)
            nova_populacao.append(child1)
            if len(nova_populacao) < TAMANHO_POPULACAO:
                nova_populacao.append(child2)
        populacao = nova_populacao

    print("EVOLUÇÃO COMPLETA")

    #Análise
    plt.figure(figsize=(10, 5))
    plt.plot(media_fitness_por_gen, marker='o')
    plt.title("Média de Fitness por Geração")
    plt.xlabel("Geração")
    plt.ylabel("Fitness Médio")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    evoluir()