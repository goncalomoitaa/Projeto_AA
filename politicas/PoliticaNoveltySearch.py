import random

from agentes.AccaoMover import AccaoMover
from politicas.PoliticaUniversalBase import PoliticaUniversalBase


class PoliticaNoveltySearch(PoliticaUniversalBase):

    def __init__(self):
        self.visitas_por_agente = {}

    def _get_visitas_agente(self, agente):
        nome = getattr(agente, "nome", str(id(agente)))
        if nome not in self.visitas_por_agente:
            self.visitas_por_agente[nome] = {}
        return self.visitas_por_agente[nome]

    @staticmethod
    def _dist_manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def escolher_accao(self, agente, observacao):
        ctx = self._extrair_contexto(agente, observacao)
        visao = ctx["visao"]
        pos_actual = ctx["pos_actual"]

        visitas = self._get_visitas_agente(agente)
        visitas[pos_actual] = visitas.get(pos_actual, 0) + 1

        # genótipo (se existir) – parâmetros evoluíveis
        genotipo = getattr(agente, "genotipo", {})
        peso_objetivo = genotipo.get("peso_objetivo", 0.0)  # 0 => “novelty puro”
        prob_random = genotipo.get("prob_random", 0.0)      # pequena aleatoriedade opcional

        # acções imediatas (recolher/depositar)
        accao_imediata = self._accao_imediata(agente, ctx)
        if accao_imediata is not None:
            return accao_imediata

        objetivos, obstaculos = self._objetivos_e_obstaculos(agente, ctx)

        # lista de candidatos
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        candidatos = []  # (di, dj, visitas_destino, dist_ao_objetivo)

        for di, dj in direcoes:
            nx, ny = agente.x + di, agente.y + dj
            nova_pos = (nx, ny)

            if nova_pos not in visao:
                continue
            if visao[nova_pos] == "OBSTACULO":
                continue

            num_visitas = visitas.get(nova_pos, 0)

            if objetivos and peso_objetivo > 0:
                dist_alvo = min(self._dist_manhattan(nova_pos, obj) for obj in objetivos)
            else:
                dist_alvo = 0

            candidatos.append((di, dj, num_visitas, dist_alvo))

        # se não há candidatos, fica tudo como dantes
        if not candidatos:
            return AccaoMover((0, 0))

        import random

        # probabilidade de movimento totalmente aleatório (exploração bruta)
        if random.random() < prob_random:
            di, dj, *_ = random.choice(candidatos)
            return AccaoMover((di, dj))

        # caso normal: “novelty puro” (ou com bias para objetivos se peso_objetivo > 0)
        def score(c):
            di, dj, v, d = c
            # quanto MENOS visitas, melhor
            # quanto MENOR distância ao objetivo, melhor (se o peso for > 0)
            return (v, peso_objetivo * d)

        candidatos.sort(key=score)
        melhores = [c for c in candidatos if score(c) == score(candidatos[0])]
        di, dj, *_ = random.choice(melhores)
        return AccaoMover((di, dj))
