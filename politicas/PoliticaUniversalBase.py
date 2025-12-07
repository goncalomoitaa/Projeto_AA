from politicas.Politica import Politica


class PoliticaUniversalBase(Politica):
    """
    Classe base para políticas universais que funcionam em:
      - AmbienteRecolecao
      - AmbienteFarol

    Fornece helpers para:
      - extrair info básica do agente+observação
      - tratar acções imediatas (recolher / depositar)
      - construir listas de objetivos e obstáculos
    As subclasses só têm de decidir COMO se movem.
    """

    def _extrair_contexto(self, agente, observacao):
        """
        Devolve um dicionário com:
          - visao
          - pos_actual
          - tipo_atual
          - tem_mochila_attr
          - mochila_valor
        """
        visao = observacao.sensores["SensorDistancia"]
        pos_actual = (agente.x, agente.y)
        tipo_atual = visao.get(pos_actual)

        tem_mochila_attr = hasattr(agente, "mochila")
        mochila_valor = getattr(agente, "mochila", 0)

        return {
            "visao": visao,
            "pos_actual": pos_actual,
            "tipo_atual": tipo_atual,
            "tem_mochila_attr": tem_mochila_attr,
            "mochila_valor": mochila_valor,
        }

    def _accao_imediata(self, agente, contexto):
        """
        Trata das acções imediatas em Recolecao:
          - se está num NINHO com mochila > 0 -> Depositar
          - se está num RECURSO com mochila == 0 -> Recolher

        Se não houver acção imediata, devolve None.
        Subclasses podem reutilizar isto directamente.
        """
        from agentes.AccaoRecolher import AccaoRecolher
        from agentes.AccaoDepositar import AccaoDepositar

        tipo_atual = contexto["tipo_atual"]
        tem_mochila_attr = contexto["tem_mochila_attr"]
        mochila_valor = contexto["mochila_valor"]

        if tem_mochila_attr:
            # Depositar
            if tipo_atual == "NINHO" and mochila_valor > 0:
                return AccaoDepositar()

            # Recolher (1 recurso de cada vez)
            if tipo_atual == "RECURSO" and mochila_valor == 0:
                return AccaoRecolher()

        return None

    def _objetivos_e_obstaculos(self, agente, contexto):
        """
        Constrói:
          - objetivos: lista de posições
          - obstaculos: conjunto de posições
        de acordo com:
          - Recoleção: mochila > 0 -> NINHO; mochila == 0 -> RECURSO
          - Farol: FAROL
        """
        visao = contexto["visao"]
        tem_mochila_attr = contexto["tem_mochila_attr"]
        mochila_valor = contexto["mochila_valor"]

        objetivos = []
        obstaculos = set()

        for (x, y), tipo in visao.items():
            if tipo == "OBSTACULO":
                obstaculos.add((x, y))
            else:
                if tem_mochila_attr:
                    # Ambiente Recolecao
                    if mochila_valor > 0:
                        # modo DEVOLVER: objetivo = NINHO
                        if tipo == "NINHO":
                            objetivos.append((x, y))
                    else:
                        # modo EXPLORAR: objetivo = RECURSO
                        if tipo == "RECURSO":
                            objetivos.append((x, y))
                else:
                    # Ambiente Farol
                    if tipo == "FAROL":
                        objetivos.append((x, y))

        return objetivos, obstaculos
