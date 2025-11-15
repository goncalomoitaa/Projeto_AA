import random

from Observacao import Observacao


# from abc import ABC, abstractmethod

class Agente:

    def __init__(self, nome: str, x: int, y: int):
        self.nome = nome
        self.x = x
        self.y = y
        self.sensores = []
        self.observacaoCurrente = None

    def observacao(self, obs: Observacao):
        self.observacaoCurrente = obs

    def age(self):
        movimento = [(0,1), (0,-1), (1,0), (-1,0)]
        return random.choice(movimento)

    def get_pos(self):
        return self.x, self.y

    def get_nome(self):
        return self.nome




