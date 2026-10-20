from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Company:
    codigo: str
    fantasia: str
    cnpj: str


@dataclass(slots=True, frozen=True)
class LoginResult:
    token: str
    company: Company
