# fusion-py

A Python client for Fusion DMS (a dealer/delivery management platform at
`fusiondms.com.br`), reverse-engineered from the browser portal's own
network traffic. There is no public API — every route here was found by
capturing real requests from the authenticated web UI.

## Architecture

- `fusion/http.py` — `HttpSession`: thin `requests.Session` wrapper. Base
  URL, timeout, retries, auth header injection, raises `FusionHTTPError` on
  non-2xx.
- `fusion/services/*.py` — one service per domain area (`auth`, `clientes`,
  `motoristas`, ...), each taking an `HttpSession` and exposing plain
  methods. Services never mutate client state themselves — they return
  plain data (`LoginResult`, `ClientesPage`, ...) and `FusionClient` applies
  it.
- `fusion/models.py` — frozen dataclasses with a `from_api(dict)`
  classmethod that normalizes the portal's raw field names/types into a
  clean public shape. Never expose the portal's raw column names on a
  public model.
- `fusion/client.py` — `FusionClient`: the public facade. Thin
  pass-through methods to each service; this is the only class most
  consumers touch.
- `fusion/grid.py` — shared helper for the portal's grid-search endpoints
  (see below). Add new entities on top of this instead of duplicating the
  request/response handling per service.

## Auth

`FusionClient.login(username, password)` drives the portal's own login
flow: GET `/login.html` to pick up fresh `AWSALB`/`AWSALBCORS` cookies,
then POST `/php/util/login.php` with `user_login`/`user_pass`. Everything
after that rides on the `requests.Session`'s cookie jar — the `Authorization:
Bearer <token>` header we also send is accepted but **not required** by at
least the grid endpoints (`get_clientes.php` works with cookies alone, no
token). Don't assume a missing/invalid token means a request will fail.

The login response is not reliable across portal instances — e.g. `cnpj`
is sometimes absent entirely. Treat every field from this endpoint as
optional and default rather than indexing it directly; see
`AuthService.login`.

## The grid-search pattern

Most "list X" screens in the portal (clients, drivers, and presumably
others we haven't captured yet — rotas, filiais, veiculos, pedidos, ...)
are backed by an endpoint shaped like:

```
POST /php/cadastros/<entity>/get_<entities>.php[?LGPD=0]
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

campo=<column>&valor=<value>&page=<n>&rows=<n>
```

Key things we've confirmed by testing live:

- **`campo` accepts any column present in the response**, not just the
  ones the screen's own UI exposes as filters. The response is a raw SQL
  join across several tables (see below), and any of those joined columns
  appears to be a valid filter — we've only confirmed one or two per
  entity, but there's no reason to expect the set is curated.
- The response is always `{"total": ..., "rows": [...]}`.
- **On zero matches, `total` and `rows` come back JSON `null`, not `0` /
  `[]`.** This crashed the client in production before the fix — always
  go through `fusion/grid.py`, which already handles it, rather than
  parsing a grid response by hand.
- Response rows are raw joined DB columns, prefixed by table alias (e.g.
  `t16_*`/`t44_*`/`t62_*` for clients, `t05_*` for drivers). These
  prefixes are internal implementation detail of their schema — always
  translate them to clean field names in a `models.py` dataclass via
  `from_api`, never expose them on the public model.
- A `Referer` header pointing at `/html/menus/main.php?menu=<slug>` is
  sent to mimic the browser, matching the clients convention
  (`menu=cadcli`). The server doesn't appear to validate its *content*,
  so an unconfirmed guess at the right menu slug for a new entity
  (`cadmot` for drivers, etc.) is a reasonable placeholder — it's cosmetic,
  not a feature.
- **`?LGPD=0` is not universal.** It's on the clients request (that screen
  shows personal data) but absent entirely from the vehicles request —
  don't assume it belongs on every grid call. `grid.search()` takes
  `params` per-call for exactly this reason; pass what was actually
  captured for that entity, not what another entity used. (The driver
  service also sends it, but only by assumption — that one was never
  independently confirmed, since we only captured its response, not its
  request.)
- Not every grid is filterable in practice: the vehicles capture used
  empty `campo`/`valor` to list everything (`&page=1&rows=250`), so
  `VeiculosService.buscar()` defaults both to `""` rather than requiring
  a filter like the other entities do. No `CAMPO_*` constant exists for
  vehicles yet because none was confirmed.
- **Don't model every joined column.** A grid response is often a join of
  several tables beyond the entity itself — e.g. the vehicles response
  also carries `t96_*` columns (the vehicle-type/`tipo_veiculo` table) and
  `t05_*` columns (the assigned driver). `Veiculo.from_api` deliberately
  keeps the `t05_*` driver fields (useful, same entity relationship as
  everywhere else) but drops `t96_*` entirely — vehicle types aren't part
  of what we're building right now. If that becomes relevant later, it's
  its own entity/service, not fields bolted onto `Veiculo`.

### Adding a new entity

Once you've captured a request for a new `get_<entity>.php` grid (DevTools
Network tab while using that screen, same way `clientes` and `motoristas`
were captured):

1. Add a model + `<Entity>Page` + `from_api` to `models.py`.
2. Add a service in `fusion/services/<entity>.py` that calls
   `fusion.grid.search(...)` and maps rows through `from_api` — see
   `clientes.py` or `motoristas.py` as the template. Don't hand-roll the
   request/response handling again.
3. Add a `CAMPO_*` constant for each filter field you've actually
   confirmed works — don't invent ones you haven't tested.
4. Wire a `buscar_<entity>` method onto `FusionClient`.
5. Write tests with `requests_mock` using real (but scrubbed of PII)
   response shapes, including the null-total/rows no-match case.
6. Field-test against the real portal before considering it done — mocked
   tests only prove the code parses what we *assume* the server sends, not
   what it actually sends. Two real bugs (`total: null`, missing `cnpj`)
   only showed up this way.

## Known routes

| Path | Service | Confirmed `campo` values |
|---|---|---|
| `/login.html` + `/php/util/login.php` | `auth.py` | n/a |
| `/php/cadastros/cliente/get_clientes.php` | `clientes.py` | `t44_codigo_erp` |
| `/php/cadastros/motorista/get_motoristas.php` | `motoristas.py` | `t05_nome`, `t05_codigo_erp` |
| `/php/cadastros/transporte/get_transportes.php` | `veiculos.py` | none confirmed — list-all only |

An earlier attempt added a client lookup against the documented
`obtemDadosBiClientes` SOAP webservice (separate login/senha credentials,
XML envelope). It was dropped once we had a confirmed, working portal
route (`get_clientes.php`) that does the same job — if a future task
needs the SOAP service specifically (e.g. it exposes data the portal
grids don't), the PDF spec for it describes the request/response
envelopes but never states the actual endpoint path, so that would need
confirming from scratch.

## Handling captured traffic

When adding new routes, captured `fetch(...)` calls and JSON responses
often carry live session cookies, tokens, and customer PII (CPF/CNPJ,
addresses, phone numbers). Scrub those before they land in test fixtures
or commit messages — fixtures in this repo use synthetic data for exactly
this reason.
