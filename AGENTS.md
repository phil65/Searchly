# AGENTS.md

## Overview

Searchly is a small async library that wraps many web/news search APIs (Brave, DataForSEO,
Exa, JigsawStack, Kagi, LinkUp, Search1API, SerpAPI, Serper, Tavily, You.com) behind two
common protocols and one set of result models, so agents can swap search backends freely.
It ships two packages: `searchly` (the clients) and `searchly_config` (lightweight pydantic
configs that build clients lazily).

## Architecture

- `src/searchly/base.py`: the core contract.
  - `WebSearchProvider` / `NewsSearchProvider`: `runtime_checkable` Protocols with
    `async web_search(...)` / `async news_search(...)` taking `query`, `max_results`,
    `country: CountryCode | None`, `language: LanguageCode | None`, `**kwargs`.
  - Result models (`schemez.Schema`, i.e. pydantic): `WebSearchResult`, `WebSearchResponse`,
    `NewsSearchResult`, `NewsSearchResponse`.
  - `CountryCode` / `LanguageCode` Literals plus `DATAFORSEO_COUNTRY_MAP`.
- `src/searchly/providers/<name>_provider/`: one client per API. Each class subclasses the
  protocol(s) it implements, reads its API key from a constructor arg or an env var, and maps
  the API's response onto the unified models. Most talk HTTP via `anyenv` (`anyenv.post_json`
  etc.); Tavily uses `httpx` directly; Brave and Exa wrap third-party SDKs (optional extras).
  Every client module ends with an `example()` coroutine runnable via `python -m`.
  - Web + news: `brave_provider/client.py`, `dataforseo_provider/dataforseo.py`,
    `serpapi_provider/client.py`, `serper_provider/client.py`, `tavily_provider/client.py`,
    `you_provider/you.py`.
  - Web only: `exa_provider/exa.py`, `jigsawstack_provider/jigsawstack.py`,
    `kagi_provider/client.py` (also `summarize()`), `linkup_provider/client.py`,
    `search1_provider/client.py`.
- `src/searchly_config/configs.py`: one `*Config` per provider (subclass of
  `BaseSearchProviderConfig`, discriminated by a `type` literal). `is_configured()` checks
  field or env var; `get_provider()` imports and instantiates the client lazily. Exposes the
  discriminated unions `WebSearchProviderConfig` / `NewsSearchProviderConfig`, the name
  Literals `WebSearchProviderName` / `NewsSearchProviderName`, and `get_config_class()`.
  It must stay importable without importing provider modules (provider imports only under
  `TYPE_CHECKING` or inside methods).
- `src/searchly/__init__.py`: re-exports everything (protocols, models, configs, clients).
- `src/searchly/exceptions.py`: errors used by the Tavily client. `src/searchly/log.py`: `get_logger`.

## Where to look

| Task | Location |
| --- | --- |
| Change the shared protocol / result models | `src/searchly/base.py` |
| Fix or extend one provider | `src/searchly/providers/<name>_provider/` |
| Add a provider | new `providers/<name>_provider/` + config in `src/searchly_config/configs.py` (add to unions and name Literals) + exports in both `__init__.py` + params in `tests/test_providers.py` |
| Provider config / env var handling | `src/searchly_config/configs.py` |
| Integration tests | `tests/test_providers.py` |
| CI | `.github/workflows/build.yml`, `.github/workflows/documentation.yml` |

## Commands

```bash
uv sync --all-extras                 # setup (extras: exa, brave_search_python_client, all)
uv run pytest                        # unit tests (integration tests deselected)
uv run pytest -m integration         # live API tests; each skips without its API key
uvx ruff check . && uvx ruff format --check .
uv run ty check                      # type check (src only); warnings fail CI
uv run mkdocs-mknodes build          # docs (or `duty build` / `duty serve`)
uv run deptry src                    # dependency hygiene
uv build
```

`duties.py` wraps these: `duty test`, `duty lint`, `duty lint_check`, `duty build`, `duty serve`,
`duty update`. Pre-commit (prek) runs ruff, tombi, ty and pytest on commit.

## Conventions

- Python >= 3.13, `from __future__ import annotations`, full type hints, Google-style docstrings.
- Ruff with a large rule set (`pyproject.toml`), line length 100, preview formatting.
- All clients are async; constructor args are keyword-only; API key falls back to an env var
  and a missing key raises `ValueError` (Tavily: `MissingAPIKeyError`).
- Unsupported filters (e.g. country/language on Exa) are accepted and ignored, so every client
  satisfies the protocol signature. Provider-specific options are extra keyword args.
- Optional SDKs (`brave_search_python_client`, `exa_py`) are imported inside `__init__`, so
  `import searchly` works without the extras; instantiating the client then raises `ImportError`.

## Pitfalls

- Copier-managed project (`.copier-answers.yml`, template `copier-phil65`): workflows,
  `duties.py`, `.pre-commit-config.yaml`, `mkdocs.yml` and most of `pyproject.toml` come from the
  template. Don't hand-edit template-owned parts; add dependencies below the
  `# Only add below (Copier)` markers. `uv.lock` is gitignored.
- `tests/test_providers.py` is marked `integration` and deselected by default
  (`addopts = ["-m", "not integration"]`); they hit real, paid APIs. Env vars:
  `BRAVE_API_KEY`, `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD`, `EXA_API_KEY`,
  `JIGSAWSTACK_API_KEY`, `KAGI_API_KEY`, `LINKUP_API_KEY`, `SEARCH1API_KEY`, `SERPAPI_KEY`,
  `SERPER_API_KEY`, `TAVILY_API_KEY`, `YOU_API_KEY`. `tests/test_searchly.py` is a placeholder so
  pytest doesn't exit with "no tests".
- Brave needs the `brave_search_python_client` extra (pulls `psutil`, which that SDK imports
  without declaring it; deptry flags it as DEP002, that's expected). Exa needs the `exa` extra
  (`exa-py>=2.0`, uses `AsyncExa.search(contents=...)`).
- `ty` checks with all extras installed; keep `# ty: ignore[...]` targeted. Mypy is no longer used.
- Docs are the mkdocs-mknodes default site: `README.md` is the index page, API pages are
  generated from docstrings. `docs/` is empty on purpose.
