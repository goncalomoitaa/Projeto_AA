from Politica import Politica

class PoliticaQLearning(Politica):
    def __init__(self, acciones, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(acciones)
        self.q_table = {}
        self.alpha = alpha  # Tasa de aprendizaje
        self.gamma = gamma  # Factor de descuento
        self.epsilon = epsilon  # Tasa de exploración

    def get_q_value(self, estado, accion):
        return self.q_table.get((estado, accion), 0.0)

    def elegir_accion(self, estado):
        import random
        if random.random() < self.epsilon:
            return random.choice(self.acciones)  # Exploración
        else:
            q_values = [self.get_q_value(estado, a) for a in self.acciones]
            max_q = max(q_values)
            mejores_acciones = [a for a, q in zip(self.acciones, q_values) if q == max_q]
            return random.choice(mejores_acciones)  # Explotación

    def actualizar(self, estado, accion, recompensa, siguiente_estado):
        max_q_siguiente = max([self.get_q_value(siguiente_estado, a) for a in self.acciones], default=0.0)
        q_valor_actual = self.get_q_value(estado, accion)
        nuevo_q_valor = q_valor_actual + self.alpha * (recompensa + self.gamma * max_q_siguiente - q_valor_actual)
        self.q_table[(estado, accion)] = nuevo_q_valor