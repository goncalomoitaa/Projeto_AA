import matplotlib.pyplot as plt
from simulador.MotorDeSimulacao import MotorDeSimulacao

class ComparacaoAlgoritmo:
    def __init__(self, ficheiro_json: str):
        self.ficheiro_json = ficheiro_json

    def correr(self):
        # --- Aleatório ---
        sim_a = MotorDeSimulacao([], None).cria(self.ficheiro_json)
        sim_a.definePolitica("PoliticaAleatoria")
        res_a = sim_a.executa()

        # --- Evolutivo ---
        sim_e = MotorDeSimulacao([], None).cria(self.ficheiro_json)
        sim_e.definePolitica("PoliticaNoveltySearch")
        res_e = sim_e.executa()

        self._imprimir(res_a, res_e)
        self._graficos(res_a, res_e)

        return res_a, res_e

    def _imprimir(self, a, e):
        print("\n=== COMPARAÇÃO ===")
        print(f"{a.nome}: taxa sucesso = {a.taxa_sucesso:.2f}% | média passos = {a.media_passos:.2f}")
        print(f"{e.nome}: taxa sucesso = {e.taxa_sucesso:.2f}%")

    def _graficos(self, a, e):
        # 1) barras: taxa de sucesso
        plt.figure(figsize=(6, 4))
        plt.bar([a.nome, e.nome], [a.taxa_sucesso, e.taxa_sucesso])
        plt.title("Taxa de sucesso (%)")
        plt.ylabel("%")
        plt.grid(True, axis="y", alpha=0.3)
        plt.show()

        # 2) passos por execução (aleatório)
        if a.passos_por_execucao:
            plt.figure(figsize=(10, 4))
            plt.plot(a.passos_por_execucao, marker='o', linestyle='-')
            plt.title("Aleatório: passos por execução")
            plt.xlabel("Execução")
            plt.ylabel("Passos")
            plt.grid(True, alpha=0.3)
            plt.show()

        # 3) fitness médio por geração (evolutivo)
        if e.fitness_medio_por_geracao:
            plt.figure(figsize=(10, 4))
            plt.plot(e.fitness_medio_por_geracao, marker='o', linestyle='-')
            plt.title("Evolutivo: fitness médio por geração")
            plt.xlabel("Geração")
            plt.ylabel("Fitness médio")
            plt.grid(True, alpha=0.3)
            plt.show()


if __name__ == "__main__":
    ComparacaoAlgoritmo("mundoFarol.json").correr()
