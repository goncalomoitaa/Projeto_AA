from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ResultadoAlgoritmo:
    nome: str
    taxa_sucesso: float
    media_passos: Optional[float] = None
    passos_por_execucao: Optional[List[int]] = None
    fitness_medio_por_geracao: Optional[List[float]] = None

