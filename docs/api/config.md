# Configuracao

O `PyWebFlxConfig` controla timeouts, retries, porta WebSocket e logging.

## Assinatura

```python
from pywebflx import PyWebFlxConfig

config = PyWebFlxConfig(
    default_timeout=10,
    delay_between_actions=0.3,
    retry_count=0,
    on_error="raise",
    ws_port=9819,
    log_level="INFO",
)
```

## Parametros

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| `default_timeout` | `float` | `10` | Timeout padrao em segundos |
| `delay_between_actions` | `float` | `0.3` | Delay entre acoes consecutivas |
| `retry_count` | `int` | `0` | Tentativas padrao em caso de falha |
| `on_error` | `str` | `"raise"` | `"raise"` ou `"continue"` |
| `ws_port` | `int` | `9819` | Porta do WebSocket server |
| `log_level` | `str` | `"INFO"` | Nivel de log |

## Prioridade

A resolucao de parametros segue esta ordem:

```
parametro da acao  >  config do use_browser  >  defaults globais
```

```python
# Global: timeout = 10 (default)
# Config: timeout = 20
# Acao: timeout = 60 (vence)

config = PyWebFlxConfig(default_timeout=20)

async with use_browser(url="https://example.com", config=config) as browser:
    await browser.click("#btn", timeout=60)  # usa 60
    await browser.click("#btn2")             # usa 20
```

## Defaults globais

```python
# Afetar todas as novas instancias
PyWebFlxConfig.set_defaults(default_timeout=15, retry_count=3)

# Resetar para os valores originais
PyWebFlxConfig.reset_defaults()
```

## Logging

```python
from pywebflx import configure_logging

configure_logging(level="INFO")                        # console (padrao)
configure_logging(level="DEBUG", sink="automacao.log") # arquivo
configure_logging(level="DISABLED")                    # silencioso
```

### Niveis

| Nivel | O que loga |
|-------|-----------|
| `ERROR` | Falha final (apos todos os retries) |
| `WARN` | Retry, reconexao, fallback |
| `INFO` | Acao executada com sucesso |
| `DEBUG` | Detalhes internos (seletor, payload JSON) |
| `TRACE` | Tudo (bytes do WebSocket, DOM parcial) |
| `DISABLED` | Nada |

### Formato

```
2026-03-28 14:32:05.123 [INFO]  [browser.click] #btn-salvar -> tab:42 -> success (120ms)
2026-03-28 14:32:06.102 [WARN]  [browser.click] #btn-enviar -> tab:42 -> retry 1/3
2026-03-28 14:32:08.001 [ERROR] [browser.extract_table] #tabela -> tab:42 -> failed: TabClosedError
```

### Override por acao

```python
await browser.click("#btn-critico", log_level="DEBUG")   # mais detalhe
await browser.click(row_selector, log_level="WARN")      # menos ruido em loop
```
