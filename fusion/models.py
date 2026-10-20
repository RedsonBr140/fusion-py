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


@dataclass(slots=True, frozen=True)
class Cliente:
    id: str
    codigo_erp: str
    cnpj: str
    fantasia: str | None
    razao_social: str
    endereco: str
    numero_endereco: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    latitude: float | None
    longitude: float | None
    segmento: str
    ativo: bool
    telefone: str | None
    email: str | None

    @classmethod
    def from_api(cls, data: dict) -> Cliente:
        return cls(
            id=data["t16_id"],
            codigo_erp=data["t44_codigo_erp"],
            cnpj=data["t16_cnpjCliente"],
            fantasia=data["t16_fantasia"] or None,
            razao_social=data["t16_razSocial"],
            endereco=data["t16_endereco"],
            numero_endereco=data["t16_numero_endereco"],
            bairro=data["t16_bairro"],
            cidade=data["t16_cidade"],
            uf=data["t16_uf"],
            cep=data["t16_cep"],
            latitude=_to_float(data.get("t44_latitude")),
            longitude=_to_float(data.get("t44_longitude")),
            segmento=data.get("t62_descricao", ""),
            ativo=data.get("t44_sn_cliente_ativo") == "S",
            telefone=data.get("t16_celular") or None,
            email=data.get("t16_email1") or None,
        )


@dataclass(slots=True, frozen=True)
class ClientesPage:
    total: int
    rows: list[Cliente]


@dataclass(slots=True, frozen=True)
class Motorista:
    id: str
    codigo_erp: str
    nome: str
    cpf: str
    telefone: str | None
    endereco: str
    uf: str
    cidade: str
    cep: str
    latitude: float | None
    longitude: float | None
    status: str
    tipo: str
    email: str | None

    @classmethod
    def from_api(cls, data: dict) -> Motorista:
        return cls(
            id=data["t05_id"],
            codigo_erp=data["t05_codigo_erp"],
            nome=data["t05_nome"],
            cpf=data["t05_cpf"],
            telefone=data.get("t05_telefone") or None,
            endereco=data["t05_endereco"],
            uf=data["t05_uf"],
            cidade=data["t05_cidade"],
            cep=data["t05_cep"],
            latitude=_to_float(data.get("t05_latitude")),
            longitude=_to_float(data.get("t05_longitude")),
            status=data.get("t05_status") or "",
            tipo=data.get("t05_tipo") or "",
            email=data.get("t05_email") or None,
        )


@dataclass(slots=True, frozen=True)
class MotoristasPage:
    total: int
    rows: list[Motorista]


def _to_float(value: str | None) -> float | None:
    return float(value) if value is not None else None
