# PyWebFlx — Design Specification

**Data:** 2026-03-28
**Status:** Draft
**Versao:** 1.0

---

## 1. Visao Geral

PyWebFlx e uma biblioteca Python para automacao web que se conecta a paginas ja abertas no Chrome, sem criar sandbox (como Selenium faz). Inspirada na UiPath, permite interagir com o DOM de qualquer pagina via uma extensao Chrome que se comunica com Python por WebSocket.

### 1.1 Problema

- Selenium exige uma instancia propria do Chrome (sandbox)
- Nao e possivel reaproveitar paginas ja abertas por outras aplicacoes
- Automacoes que dependem de sessao/login ativo nao funcionam bem com Selenium

### 1.2 Solucao

- Extensao Chrome (Manifest V3) que acessa o DOM de qualquer aba
- Python atua como WebSocket server, extensao conecta como client
- API async inspirada na UiPath (click, type_into, get_text, inspect, extract_table, etc.)
- Funcao `inspect` otimizada para uso com IAs (estrutura resumida do DOM)

### 1.3 Publico-Alvo

- Desenvolvedores Python que precisam automatizar paginas web ja abertas
- Times de RPA que buscam alternativa ao UiPath com controle programatico
- Fluxos de automacao assistidos por IA

---

## 2. Arquitetura

### 2.1 Diagrama

```
+--------------------------------------------------+
|  Script do Usuario (Python)                      |
|                                                  |
|  async with use_browser(url="sicoob") as b:      |
|      await b.click(text="Entrar")                |
|      saldo = await b.get_text(".saldo")          |
+-------------------+------------------------------+
                    | API async (pywebflx)
                    v
+--------------------------------------------------+
|  PyWebFlx Server (Python)                        |
|  +-------------+ +------------+ +--------------+ |
|  | WebSocket   | | Tab        | | Command      | |
|  | Server      | | Manager    | | Dispatcher   | |
|  | :9819       | |            | |              | |
|  +------+------+ +------------+ +--------------+ |
+---------|-----------------------------------------+
          | ws://localhost:9819
          v
+--------------------------------------------------+
|  Extensao Chrome (Manifest V3)                   |
|  +-------------+ +----------------------------+ |
|  | background  | | content scripts            | |
|  | .js         |-| (injetados sob demanda     | |
|  | WS Client   | |  via chrome.scripting)     | |
|  | + keepalive | |  executam no DOM da aba     | |
|  +-------------+ +----------------------------+ |
+--------------------------------------------------+
```

### 2.2 Abordagem Escolhida

**Python como WebSocket server, extensao como client.**

Razoes:
- Evita limitacao do Manifest V3 (service workers nao podem abrir server sockets)
- Python tem controle total como server — pode gerenciar multiplas extensoes/abas
- Sem componentes intermediarios (sem Native Messaging, sem Registry)
- Setup simples: instala extensao, roda Python, pronto

### 2.3 Fluxo de um Comando

1. Python chama `await browser.click("#btn")`
2. PyWebFlx serializa: `{"id": "cmd_1", "action": "click", "tabId": 42, "params": {...}}`
3. Envia via WebSocket para extensao `background.js`
4. Background injeta/executa script na aba 42 via `chrome.scripting.executeScript`
5. Resultado volta: `{"id": "cmd_1", "success": true}` ou `{"id": "cmd_1", "error": "..."}`
6. Python resolve o `await` com o resultado

### 2.4 Reconexao e Resiliencia

- Extensao tenta conectar ao Python a cada 3 segundos se desconectada
- `chrome.alarms` a cada 25s mantém o service worker vivo
- Se a aba alvo fecha, extensao notifica Python via evento `tab_closed`
- Comandos com `tabId` invalido retornam `TabNotFoundError`

---

## 3. Extensao Chrome

### 3.1 Estrutura

```
extension/
  manifest.json          # Manifest V3, permissoes
  background.js          # Service worker: WS client, coordenador
  content.js             # Injetado sob demanda: executa no DOM
  icons/                 # Icone da extensao (16, 48, 128px)
```

### 3.2 Manifest V3

```json
{
  "manifest_version": 3,
  "name": "PyWebFlx Bridge",
  "version": "1.0.0",
  "description": "Bridge between PyWebFlx Python library and Chrome",
  "permissions": [
    "tabs",
    "scripting",
    "activeTab",
    "downloads",
    "alarms"
  ],
  "host_permissions": ["<all_urls>"],
  "background": {
    "service_worker": "background.js"
  }
}
```

### 3.3 background.js — Responsabilidades

- WebSocket client: conecta em `ws://localhost:9819` (configuravel)
- Keep-alive: `chrome.alarms` a cada 25s
- Dispatcher: recebe comandos JSON do Python, roteia para aba correta
- Tab Manager: busca abas por titulo/URL, cria novas abas, reporta eventos

### 3.4 Injecao de Scripts

Nao usa content script persistente. O `background.js` injeta funcoes especificas via `chrome.scripting.executeScript` conforme o comando recebido. Cada acao e uma execucao isolada.

### 3.5 Protocolo de Comunicacao (JSON)

**Comando (Python -> Extensao):**

```json
{
  "id": "cmd_123",
  "action": "click",
  "tabId": 42,
  "params": {
    "selector": "#btn",
    "selectorType": "css",
    "clickType": "single",
    "mouseButton": "left"
  }
}
```

**Resposta sucesso (Extensao -> Python):**

```json
{
  "id": "cmd_123",
  "success": true,
  "data": null
}
```

**Resposta erro (Extensao -> Python):**

```json
{
  "id": "cmd_123",
  "success": false,
  "error": "ElementNotFoundError",
  "message": "Selector '#btn' not found within 10s"
}
```

**Evento nao-solicitado (Extensao -> Python):**

```json
{
  "event": "tab_closed",
  "tabId": 42
}
```

---

## 4. API Python

### 4.1 Conexao e Gerenciamento de Browser

```python
from pywebflx import use_browser, BrowserNotFoundError

# Conectar por URL (parcial)
async with use_browser(url="sicoob.com.br") as browser:
    ...

# Conectar por titulo
async with use_browser(title="Portal Sicoob") as browser:
    ...

# Conectar com fallback (if_not_open)
async with use_browser(
    url="sicoob.com.br",
    title="Portal Sicoob",
    if_not_open="https://portal.sicoob.com.br/login"
) as browser:
    ...

# Se nao encontrar e if_not_open nao definido -> BrowserNotFoundError
```

**Logica do if_not_open (lado Python):**

1. Python pergunta a extensao: "tem aba com titulo X ou URL Y?"
2. Se sim -> conecta
3. Se nao e `if_not_open` definido:
   - Chrome aberto -> extensao cria nova aba com a URL
   - Chrome fechado -> Python abre Chrome via subprocess, espera extensao conectar, cria aba
4. Se nao e `if_not_open` nao definido -> lanca `BrowserNotFoundError`

### 4.2 Navegacao

```python
await browser.navigate_to("https://portal.sicoob.com.br/dashboard")
await browser.go_back()
await browser.go_forward()
await browser.refresh()
await browser.close_tab()
await browser.close_browser()
```

### 4.3 Interacao com Elementos

**Seletores flexiveis:** CSS, XPath, ou atributos humanizados.

```python
# CSS
await browser.click("#btn-login")

# XPath
await browser.click("//button[@id='submit']")

# Atributos humanizados
await browser.click(text="Entrar", tag="button")
```

**Click avancado:**

```python
await browser.click("#menu", click_type="double", delay_after=0.5)
await browser.click("#item", mouse_button="right")
await browser.click("#btn", retry=3, verify=".sucesso", timeout=10)
```

**Digitacao:**

```python
await browser.type_into("#email", "usuario@sicoob.com.br")
await browser.type_into("#senha", "123", delay_between_keys=0.05)
```

**Set text (sem simular digitacao):**

```python
await browser.set_text("#campo", "valor direto")
```

**Checkbox, dropdown, hover, hotkeys:**

```python
await browser.check("#aceito-termos")
await browser.uncheck("#newsletter")
await browser.select_item("#estado", "Para", by="text")
await browser.hover("#menu-dropdown")
await browser.send_hotkey("ctrl+a")
await browser.send_hotkey("Enter")
```

### 4.4 Extracao de Dados

```python
texto = await browser.get_text(".saldo-conta")
href = await browser.get_attribute("a.link-relatorio", "href")
html = await browser.get_full_text()
```

**Extract Table com paginacao:**

```python
# Tabela HTML simples
dados = await browser.extract_table("#tabela-clientes")
# [{"Nome": "Joao", "Saldo": "1.200,00"}, ...]

# Com paginacao automatica
dados = await browser.extract_table(
    "#tabela-clientes",
    next_page="#btn-proxima",
    max_pages=10
)

# Dados estruturados nao-<table> (cards, divs repetitivas)
dados = await browser.extract_data(
    container="#lista-resultados",
    row=".card-cliente",
    columns={
        "Nome": ".card-title",
        "CPF": ".card-cpf",
        "Saldo": ".card-saldo span"
    },
    next_page="#btn-proxima"
)
```

**Screenshot:**

```python
await browser.take_screenshot("relatorio.png")
await browser.take_screenshot("elemento.png", selector="#grafico")
```

### 4.5 Inspect — Visao do DOM para IAs

Retorna estrutura resumida do DOM otimizada para consumo por IAs.

```python
# Pagina inteira
estrutura = await browser.inspect()

# Escopo especifico
estrutura = await browser.inspect("#login-form")

# Com controle de profundidade e amostras
estrutura = await browser.inspect("#tabela", depth=3, samples=5)
```

**Exemplo de saida do inspect:**

```
<body>
  <header#top-nav .navbar>
    <button.btn-menu> "Menu"
    <input#search type="search" placeholder="Buscar...">
    <a.logo> "Portal Sicoob"
  </header>
  <main#content>
    <form#login-form>
      <input#usuario type="text" placeholder="Usuario" [required]>
      <input#senha type="password" placeholder="Senha" [required]>
      <select#agencia> 3 options: ["0001 - Centro", "0032 - Belem", "0045 - Maraba"]
      <button#btn-login type="submit"> "Entrar"
    </form>
    <div.avisos>
      <table#tabela-avisos> 3 cols x 12 rows
    </div>
  </main>
</body>
```

### 4.6 Espera e Sincronizacao

```python
existe = await browser.element_exists("#modal-sucesso", timeout=5)
await browser.wait_element("#loading", condition="visible", timeout=10)
await browser.wait_element_vanish("#spinner", timeout=15)
elem = await browser.find_element("#campo-nome")
```

### 4.7 JavaScript e Iframes

```python
resultado = await browser.execute_js("return document.title")
await browser.inject_js("window.scrollTo(0, document.body.scrollHeight)")

async with browser.switch_to("#iframe-conteudo") as frame:
    await frame.click("#btn-dentro-do-iframe")
```

### 4.8 Downloads e Uploads

```python
await browser.set_file("#input-upload", "C:/docs/relatorio.pdf")

async with browser.wait_for_download(timeout=30) as download:
    await browser.click("#btn-download")
    caminho = download.path
```

### 4.9 Multiplas Abas Simultaneas

```python
async with use_browser(url="portal") as aba1:
    async with use_browser(url="email") as aba2:
        dado = await aba1.get_text(".saldo")
        await aba2.type_into("#corpo", dado)
```

---

## 5. Excecoes

### 5.1 Hierarquia

```
PyWebFlxError (base)
  ConnectionError
    ExtensionNotConnectedError
    ConnectionLostError
  BrowserError
    BrowserNotFoundError
    TabNotFoundError
    TabClosedError
  ElementError
    ElementNotFoundError
    ElementTimeoutError
    ElementNotInteractableError
    SelectorError
  ActionError
    NavigationError
    InjectionError
    DownloadError
    ScreenshotError
  ConfigError
```

### 5.2 Contexto nas Excecoes

Cada excecao carrega informacoes relevantes:

```python
try:
    await browser.click("#btn-inexistente")
except ElementNotFoundError as e:
    e.selector    # "#btn-inexistente"
    e.tab_id      # 42
    e.timeout     # 10
    e.message     # "Selector '#btn-inexistente' not found within 10s"
```

---

## 6. Logging

### 6.1 Formato Padrao

```
2026-03-28 14:32:05.123 [INFO]  [browser.click] #btn-salvar -> tab:42 -> success (120ms)
2026-03-28 14:32:05.450 [INFO]  [browser.type_into] #email -> "joao@sicoob.com.br" -> tab:42 -> success (85ms)
2026-03-28 14:32:06.102 [WARN]  [browser.click] #btn-enviar -> tab:42 -> retry 1/3 (ElementNotInteractableError)
2026-03-28 14:32:07.540 [INFO]  [browser.click] #btn-enviar -> tab:42 -> success (retry 2, 340ms)
2026-03-28 14:32:08.001 [ERROR] [browser.extract_table] #tabela -> tab:42 -> failed: TabClosedError
```

### 6.2 Niveis

| Nivel | O que loga |
|-------|-----------|
| ERROR | Falha final (apos todos os retries) |
| WARN  | Retry, reconexao, fallback |
| INFO  | Acao executada com sucesso |
| DEBUG | Detalhes internos: seletor resolvido, payload JSON, tempo de cada etapa |
| TRACE | Tudo: bytes do WebSocket, DOM parcial retornado, cada tentativa de resolucao |

### 6.3 Configuracao

```python
from pywebflx import configure_logging

configure_logging(level="INFO")                          # console (padrao)
configure_logging(level="DEBUG", sink="automacao.log")   # arquivo
configure_logging(level="DISABLED")                      # silencioso
configure_logging(handler=meu_handler)                   # handler customizado
configure_logging(timestamp_format="%H:%M:%S")           # formato compacto
```

### 6.4 Sobrescrita por Acao

```python
await browser.click("#btn-critico", log_level="DEBUG")    # mais detalhe nesta acao
await browser.click(row_selector, log_level="WARN")       # menos ruido em loop
```

### 6.5 Implementacao

Decorator interno `@_logged_action` em cada metodo:

```python
@_logged_action("browser.click")
async def click(self, selector, **kwargs):
    ...
```

O decorator mede tempo, loga entrada/saida/erro/retry automaticamente. Timestamp `YYYY-MM-DD HH:MM:SS.mmm` com milissegundos por padrao.

---

## 7. Configuracao Global

```python
from pywebflx import PyWebFlxConfig

# Via construtor
async with use_browser(
    url="sicoob.com.br",
    config=PyWebFlxConfig(
        default_timeout=10,
        delay_between_actions=0.3,
        retry_count=2,
        on_error="continue",
        ws_port=9819,
        log_level="INFO"
    )
) as browser:
    ...

# Ou defaults globais
PyWebFlxConfig.set_defaults(
    default_timeout=15,
    retry_count=3
)
```

**Prioridade:** parametro da acao > config do use_browser > defaults globais

---

## 8. Estrutura do Projeto

```
pywebflx/
  pyproject.toml
  src/
    pywebflx/
      __init__.py           # exports publicos
      browser.py            # use_browser, BrowserContext
      actions.py            # click, type_into, get_text, inspect, extract_table...
      selectors.py          # resolucao CSS/XPath/atributos humanizados
      connection.py         # WebSocket server
      config.py             # PyWebFlxConfig
      logging.py            # configure_logging, decorator @_logged_action
      exceptions.py         # hierarquia de excecoes
      cli.py                # install-extension command
  extension/
    manifest.json
    background.js
    content.js
    icons/
  tests/
  docs/
    backlog.md              # funcionalidades futuras (v2)
```

---

## 9. CLI — Instalacao da Extensao

```bash
# Instala/guia instalacao da extensao no Chrome
pywebflx install-extension

# Verifica se extensao esta instalada e conectando
pywebflx check
```

O comando `install-extension`:
1. Localiza o diretorio da extensao empacotada junto com a lib
2. Abre `chrome://extensions` no Chrome
3. Instrui o usuario a habilitar modo desenvolvedor e carregar a extensao descompactada
4. Verifica conexao WebSocket apos instalacao

---

## 10. Backlog v2

Funcionalidades planejadas para versoes futuras, documentadas em `docs/backlog.md`:

- `for_each` com paginacao automatica (`next_page=`)
- `assert_text`, `assert_visible` (verificacoes explicitas)
- `on_element_appear` / `on_element_vanish` (triggers por evento)
- Native Messaging como alternativa ao WebSocket
- Publicacao na Chrome Web Store
- Suporte a Firefox (WebExtensions API)
- Screen Scraping via OCR

---

## 11. Decisoes de Design

| Decisao | Escolha | Alternativa descartada | Razao |
|---------|---------|----------------------|-------|
| Comunicacao | WebSocket | Native Messaging | Simplicidade de setup, sem Registry |
| Direcao WS | Python=server, extensao=client | Inverso | Manifest V3 nao permite server no service worker |
| API | Async/await | Sincrona | Moderno, bom para esperas e paralelismo |
| Seletores | CSS + XPath + atributos | Apenas CSS | XPath necessario para casos complexos, atributos humanizados melhoram DX |
| Logging | Loguru com fallback | stdlib logging | Melhor DX, cores, niveis (TRACE), mas com fallback para stdlib |
| Excecoes | Customizadas (PyWebFlxError) | Reusar Selenium | Produto novo, identidade propria |
| Distribuicao | Lib publica (preparar para PyPI) | Uso interno apenas | Estrutura pronta para abrir sem retrabalho |
| Instalacao extensao | CLI assistido | Manual ou Chrome Web Store | Bom equilibrio entre DX e complexidade |
| Inspect | Estrutura resumida do DOM | outerHTML bruto | 95% menos tokens para IAs, mesma informacao util |
