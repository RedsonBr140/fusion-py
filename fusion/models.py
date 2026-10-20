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


@dataclass(slots=True, frozen=True)
class Veiculo:
    id: str
    codigo_erp: str
    descricao: str
    placa: str
    status: str
    modelo: str
    ano_modelo: str
    ano_fabricacao: str
    km_atual: int | None
    tipo_combustivel: str
    proprio: bool
    latitude: float | None
    longitude: float | None
    motorista_id: str | None
    motorista_nome: str | None

    @classmethod
    def from_api(cls, data: dict) -> Veiculo:
        # t96_* columns (tipo de veiculo join) are deliberately left out —
        # out of scope for what we're building right now.
        return cls(
            id=data["t06_id"],
            codigo_erp=data["t06_codigo_erp"],
            descricao=data["t06_descricao"],
            placa=data["t06_placa"],
            status=data.get("t06_status") or "",
            modelo=data.get("t06_modelo") or "",
            ano_modelo=data.get("t06_anoModelo") or "",
            ano_fabricacao=data.get("t06_anoFabricacao") or "",
            km_atual=_to_int(data.get("t06_kmAtual")),
            tipo_combustivel=data.get("t06_tipo_combustivel") or "",
            proprio=data.get("t06_sn_proprio") == "S",
            latitude=_to_float(data.get("t06_latitudeAtual")),
            longitude=_to_float(data.get("t06_longitudeAtual")),
            motorista_id=data.get("t05_id") or None,
            motorista_nome=data.get("t05_nome") or None,
        )


@dataclass(slots=True, frozen=True)
class VeiculosPage:
    total: int
    rows: list[Veiculo]


def _to_float(value: str | None) -> float | None:
    return float(value) if value is not None else None


def _to_int(value: str | None) -> int | None:
    return int(value) if value is not None else None
