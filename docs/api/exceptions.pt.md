# Excecoes

Todas as excecoes herdam de `PyWebFlxError` e possuem atributos contextuais.

## Hierarquia

```
PyWebFlxError
+-- ConnectionError
|   +-- ExtensionNotConnectedError
|   +-- ConnectionLostError
+-- BrowserError
|   +-- BrowserNotFoundError
|   +-- TabNotFoundError
|   +-- TabClosedError
+-- ElementError
|   +-- ElementNotFoundError
|   +-- ElementTimeoutError
|   +-- ElementNotInteractableError
|   +-- SelectorError
+-- ActionError
|   +-- NavigationError
|   +-- InjectionError
|   +-- DownloadError
|   +-- ScreenshotError
+-- ConfigError
```

## Atributos contextuais

Cada excecao carrega informacoes relevantes para depuracao:

```python
try:
    await browser.click("#nonexistent-btn")
except ElementNotFoundError as e:
    print(e.selector)   # "#nonexistent-btn"
    print(e.tab_id)     # 42
    print(e.timeout)    # 10
    print(e.message)    # "Element '#nonexistent-btn' not found within 10s"
```

## Referencia

### Conexao

| Excecao | Quando | Atributos |
|---------|--------|-----------|
| `ExtensionNotConnectedError` | Extensao nao conectou a tempo | `port`, `timeout` |
| `ConnectionLostError` | WebSocket caiu durante operacao | `reason` |

### Navegador

| Excecao | Quando | Atributos |
|---------|--------|-----------|
| `BrowserNotFoundError` | Nenhuma aba encontrada | `title`, `url` |
| `TabNotFoundError` | Aba especifica nao encontrada | `title`, `url` |
| `TabClosedError` | Aba fechou durante operacao | `tab_id` |

### Elemento

| Excecao | Quando | Atributos |
|---------|--------|-----------|
| `ElementNotFoundError` | Seletor nao encontrou elemento | `selector`, `tab_id`, `timeout` |
| `ElementTimeoutError` | Timeout aguardando condicao | `selector`, `tab_id`, `timeout`, `condition` |
| `ElementNotInteractableError` | Elemento nao clicavel | `selector`, `tab_id`, `reason` |
| `SelectorError` | Seletor invalido | `selector`, `reason` |

### Acao

| Excecao | Quando | Atributos |
|---------|--------|-----------|
| `NavigationError` | Falha ao navegar | `url`, `reason` |
| `InjectionError` | Falha ao injetar script | `tab_id`, `reason` |
| `DownloadError` | Download falhou/timeout | `timeout`, `reason` |
| `ScreenshotError` | Screenshot falhou | `path`, `reason` |

### Configuracao

| Excecao | Quando | Atributos |
|---------|--------|-----------|
| `ConfigError` | Valor de configuracao invalido | `param`, `value`, `reason` |

## Exemplo completo

```python
from pywebflx import use_browser, BrowserNotFoundError, ElementNotFoundError

try:
    async with use_browser(url="portal.com", open="never") as browser:
        try:
            await browser.click("#btn-login", timeout=5)
        except ElementNotFoundError as e:
            print(f"Botao {e.selector} nao encontrado na aba {e.tab_id}")
except BrowserNotFoundError as e:
    print(f"Nenhuma aba com url={e.url}")
```
