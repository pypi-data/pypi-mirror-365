import sympy
from typing import List, Tuple


type Monomial = str


def caos(monomials: List[Monomial], theta: float) -> List[Tuple[Monomial, float]]:
    
    eqn = """\\forall """