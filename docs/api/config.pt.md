# Configuração

`PyWebFlxConfig` controla timeouts, retentativas, porta WebSocket e logging.

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

## Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `default_timeout` | `float` | `10` | Timeout padrão em segundos |
| `delay_between_actions` | `float` | `0.3` | Atraso entre ações consecutivas |
| `retry_count` | `int` | `0` | Tentativas de retentativa padrão em caso de falha |
| `on_error` | `str` | `"raise"` | `"raise"` ou `"continue"` |
| `ws_port` | `int` | `9819` | Porta do servidor WebSocket |
| `log_level` | `str` | `"INFO"` | Nível de log |

## Prioridade

A resolução de parâmetros segue esta ordem:

```
parâmetro da ação  >  config do use_browser  >  padrões globais
```

```python
# Global: timeout = 10 (padrão)
# Config: timeout = 20
# Ação: timeout = 60 (vence)

config = PyWebFlxConfig(default_timeout=20)

async with use_browser(url="https://example.com", config=config) as browser:
    await browser.click("#btn", timeout=60)  # usa 60
    await browser.click("#btn2")             # usa 20
```

## Padrões globais

```python
# Afeta todas as novas instancias
PyWebFlxConfig.set_defaults(default_timeout=15, retry_count=3)

# Resetar para valores originais
PyWebFlxConfig.reset_defaults()
```

## Logging

```python
from pywebflx import configure_logging

configure_logging(level="INFO")                        # console (padrão)
configure_logging(level="DEBUG", sink="automation.log") # arquivo
configure_logging(level="DISABLED")                    # silencioso
```

### Níveis

| Nível | O que registra |
|-------|----------------|
| `ERROR` | Falha final (após todas as retentativas) |
| `WARN` | Retentativa, reconexão, fallback |
| `INFO` | Ação executada com sucesso |
| `DEBUG` | Detalhes internos (seletor, payload JSON) |
| `TRACE` | Tudo (bytes WebSocket, DOM parcial) |
| `DISABLED` | Nada |

### Formato

```
2026-03-28 14:32:05.123 [INFO]  [browser.click] #btn-save -> tab:42 -> sucesso (120ms)
2026-03-28 14:32:06.102 [WARN]  [browser.click] #btn-send -> tab:42 -> retentativa 1/3
2026-03-28 14:32:08.001 [ERROR] [browser.extract_table] #table -> tab:42 -> falhou: TabClosedError
```

### Override por ação

```python
await browser.click("#critical-btn", log_level="DEBUG")   # mais detalhes
await browser.click(row_selector, log_level="WARN")       # menos ruído em loops
```
