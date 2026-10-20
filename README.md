# fusion-py

Cliente Python não-oficial para o **Fusion DMS** (`fusiondms.com.br`), um
sistema de gestão de entregas/transportadoras.

Não existe uma API pública documentada para o que esta biblioteca faz — as
rotas aqui foram descobertas capturando o tráfego real do próprio portal
web autenticado (DevTools → Network). Trate-a como tal: comportamento do
servidor pode mudar sem aviso, e campos/filtros marcados como "não
confirmados" no código são justamente isso.

## Instalação

```bash
pip install fusiondms-client
```

O nome do pacote no PyPI é `fusiondms-client`, mas o import continua sendo
`fusion` (ex.: `from fusion import FusionClient`).

Enquanto não publicado, ou para acompanhar o `main` direto:

```bash
pip install git+ssh://git@github.com/RedsonBr140/fusion-py.git
```

Para desenvolvimento local lado a lado com outro projeto:

```bash
pip install -e /caminho/para/fusion-py
```

Requer Python 3.10+.

## Uso básico

```python
from fusion import FusionClient
from fusion.services.clientes import CAMPO_CODIGO_ERP

with FusionClient("downloads") as client:
    client.login("usuario", "senha")
    print(client.company)  # Company(codigo=..., fantasia=..., cnpj=...)

    pagina = client.buscar_clientes(CAMPO_CODIGO_ERP, "73967")
    for cliente in pagina.rows:
        print(cliente.razao_social, cliente.cidade)
```

`FusionClient` é um gerenciador de contexto (`with`) e fecha a sessão HTTP
automaticamente ao sair do bloco. `download_dir` é criado se não existir —
ele **nunca** apaga arquivos já presentes.

## O que já está implementado

| Entidade | Método | Rota |
|---|---|---|
| Autenticação | `client.login(usuario, senha)` | `/login.html` + `/php/util/login.php` |
| Clientes | `client.buscar_clientes(campo, valor, *, page=1, rows=10)` | `/php/cadastros/cliente/get_clientes.php` |
| Motoristas | `client.buscar_motoristas(campo, valor, *, page=1, rows=10)` | `/php/cadastros/motorista/get_motoristas.php` |
| Veículos | `client.buscar_veiculos(campo="", valor="", *, page=1, rows=10)` | `/php/cadastros/transporte/get_transportes.php` |

Cada busca retorna uma página (`ClientesPage`, `MotoristasPage`,
`VeiculosPage`) com `.total` e `.rows`, onde cada linha já vem convertida
para um dataclass tipado (`Cliente`, `Motorista`, `Veiculo`) — os nomes de
coluna brutos do banco do Fusion (`t16_*`, `t44_*`, `t05_*`, ...) não
vazam para quem usa a biblioteca.

### Filtros (`campo`/`valor`)

As telas de listagem do portal aceitam filtrar por **qualquer coluna
presente na resposta**, não só pelas que a própria tela expõe como filtro
na UI. Cada serviço expõe constantes `CAMPO_*` para os campos já
confirmados por teste real:

```python
from fusion.services.clientes import CAMPO_CODIGO_ERP
from fusion.services.motoristas import CAMPO_NOME, CAMPO_CODIGO_ERP as CAMPO_CODIGO_ERP_MOTORISTA
```

Nada impede passar uma string arbitrária como `campo` se você descobrir
(e confirmar) um novo filtro válido — só não existe constante nomeada
para ele ainda.

### Erros

```python
from fusion import FusionError, FusionAuthError, FusionHTTPError
```

- `FusionAuthError` — login falhou (credenciais inválidas, etc).
- `FusionHTTPError` — a requisição HTTP retornou status de erro
  (`status_code` e `response` disponíveis na exceção).
- `FusionError` — erro genérico de resposta inesperada do portal.

## Configuração

```python
from fusion import FusionClient, FusionConfig

client = FusionClient(
    "downloads",
    config=FusionConfig(timeout=60, max_retries=3),
)
```

## Rodando os testes

```bash
python -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/pytest
```

Os testes usam `requests-mock` com dados sintéticos — nenhum teste bate no
portal real. Para validar contra o Fusion de verdade, é preciso rodar um
script manual com credenciais reais via variável de ambiente (veja
`CLAUDE.md` para o padrão usado durante o desenvolvimento).

## Para quem for estender esta lib

O arquivo [`CLAUDE.md`](./CLAUDE.md) documenta o padrão das rotas de
listagem (`get_<entidade>.php`), as particularidades já descobertas
(ex.: `total`/`rows` voltam `null` em vez de `0`/`[]` quando não há
resultado, `?LGPD=0` não é universal) e o passo a passo para adicionar uma
nova entidade seguindo o mesmo template.

## Aviso

Este projeto não é afiliado, endossado ou mantido pela NSTECH/Fusion DMS.
Foi construído por engenharia reversa do tráfego de um portal autenticado
para automatizar um fluxo de trabalho legítimo e com credenciais próprias
— use por sua conta e risco, e respeite os termos de uso do seu contrato
com o Fusion DMS.
