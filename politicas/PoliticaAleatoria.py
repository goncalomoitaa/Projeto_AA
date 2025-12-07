import random

from agentes.AccaoMover import AccaoMover
from politicas.PoliticaUniversalBase import PoliticaUniversalBase


class PoliticaAleatoria(PoliticaUniversalBase):
    """
    Política universal “simples”:

    - usa a lógica base da PoliticaUniversalBase para:
        * acções imediatas (recolher/depositar)
        * lista de objetivos e obstáculos
    - se houver objetivos:
        * vai greedy para o objetivo mais próximo
    - senão:
        * movimento aleatório evitando obstáculos
    """

    def escolher_accao(self, agente, observacao):
        # 1) contexto básico (visão, posição, etc.)
        ctx = self._extrair_contexto(agente, observacao)

        # 2) acções imediatas (recolher / depositar)
        accao_imediata = self._accao_imediata(agente, ctx)
        if accao_imediata is not None:
            return accao_imediata

        # 3) objetivos e obstáculos
        objetivos, obstaculos = self._objetivos_e_obstaculos(agente, ctx)
        visao = ctx["visao"]

        # 4) Se houver objetivos, ir greedy ao mais próximo
        if objetivos:
            alvo = min(
                objetivos,
                key=lambda pos: abs(pos[0] - agente.x) + abs(pos[1] - agente.y)
            )

            dx = alvo[0] - agente.x
            dy = alvo[1] - agente.y

            i = 0 if dx == 0 else (1 if dx > 0 else -1)
            j = 0 if dy == 0 else (1 if dy > 0 else -1)

            nova_pos = (agente.x + i, agente.y + j)
            if nova_pos not in obstaculos and visao.get(nova_pos) != "OBSTACULO":
                return AccaoMover((i, j))

        # 5) Caso não haja objetivos, movimento aleatório que não seja obstáculo
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(direcoes)

        for di, dj in direcoes:
            nova_pos = (agente.x + di, agente.y + dj)
            if visao.get(nova_pos) != "OBSTACULO":
                return AccaoMover((di, dj))

        # 6) Se não houver nenhuma direção possível, fica parado
        return AccaoMover((0, 0))
