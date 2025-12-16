from agentes.Agente import Agente


class AgenteFarol(Agente):

    def __init__(self, nome, x, y):
        super().__init__(nome, x, y)
        self.mochila = 0

    def age(self):
        accao = self.politica.escolher_accao(self)
        return accao

    def avaliacaoEstadoAtual(self, recompensa):
        # AQUI ESTÁ A CORREÇÃO:
        # Temos de chamar o método 'aprender' para atualizar a Tabela Q
        if hasattr(self.politica, 'aprender'):
            self.politica.aprender(self, recompensa)