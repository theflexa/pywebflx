# Exceções

Todas as exceções herdam de `PyWebFlxError` e possuem atributos contextuais.

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

Cada exceção carrega informações relevantes para depuração:

```python
try:
    await browser.click("#nonexistent-btn")
except ElementNotFoundError as e:
    print(e.selector)   # "#nonexistent-btn"
    print(e.tab_id)     # 42
    print(e.timeout)    # 10
    print(e.message)    # "Element '#nonexistent-btn' not found within 10s"
```

## Referência

### Conexão

| Exceção | Quando | Atributos |
|---------|--------|-----------|
| `ExtensionNotConnectedError` | Extensão não conectou a tempo | `port`, `timeout` |
| `ConnectionLostError` | WebSocket caiu durante operação | `reason` |

### Navegador

| Exceção | Quando | Atributos |
|---------|--------|-----------|
| `BrowserNotFoundError` | Nenhuma aba encontrada | `title`, `url` |
| `TabNotFoundError` | Aba específica não encontrada | `title`, `url` |
| `TabClosedError` | Aba fechou durante operação | `tab_id` |

### Elemento

| Exceção | Quando | Atributos |
|---------|--------|-----------|
| `ElementNotFoundError` | Seletor não encontrou elemento | `selector`, `tab_id`, `timeout` |
| `ElementTimeoutError` | Timeout aguardando condição | `selector`, `tab_id`, `timeout`, `condition` |
| `ElementNotInteractableError` | Elemento não clicável | `selector`, `tab_id`, `reason` |
| `SelectorError` | Seletor inválido | `selector`, `reason` |

### Ação

| Exceção | Quando | Atributos |
|---------|--------|-----------|
| `NavigationError` | Falha ao navegar | `url`, `reason` |
| `InjectionError` | Falha ao injetar script | `tab_id`, `reason` |
| `DownloadError` | Download falhou/timeout | `timeout`, `reason` |
| `ScreenshotError` | Screenshot falhou | `path`, `reason` |

### Configuração

| Exceção | Quando | Atributos |
|---------|--------|-----------|
| `ConfigError` | Valor de configuração inválido | `param`, `value`, `reason` |

## Exemplo completo

```python
from pywebflx import use_browser, BrowserNotFoundError, ElementNotFoundError

try:
    async with use_browser(url="portal.com", open="never") as browser:
        try:
            await browser.click("#btn-login", timeout=5)
        except ElementNotFoundError as e:
            print(f"Botão {e.selector} não encontrado na aba {e.tab_id}")
except BrowserNotFoundError as e:
    print(f"Nenhuma aba com url={e.url}")
```
