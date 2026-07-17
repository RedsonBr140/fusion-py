from dataclasses import dataclass


@dataclass(slots=True)
class Company:
    codigo: str
    fantasia: str
    cnpj: str