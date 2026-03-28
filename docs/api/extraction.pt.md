# Extração de Dados

Métodos para extrair texto, atributos e dados estruturados da página.

---

## get_text

Retorna o texto visível de um elemento.

```python
text = await browser.get_text(selector)
```

### Exemplo

```python
saldo = await browser.get_text(".account-balance")
# "R$ 1.200,00"

título = await browser.get_text("h1")
# "Painel"
```

---

## get_attribute

Retorna o valor de um atributo HTML.

```python
value = await browser.get_attribute(selector, attribute="name")
```

### Exemplo

```python
href = await browser.get_attribute("a.report", attribute="href")
# "https://portal.com/report.pdf"

css_class = await browser.get_attribute("#btn", attribute="class")
# "btn btn-primary"
```

---

## get_full_text

Retorna todo o texto visível da página.

```python
text = await browser.get_full_text()
```

---

## extract_data

Extrai dados estruturados de elementos repetitivos (cards, listas, divs).

```python
data = await browser.extract_data(
    container="seletor-pai",
    row="seletor-de-cada-item",
    columns={"nome_coluna": "seletor-interno"},
)
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `container` | `str` | `""` | Seletor do container pai |
| `row` | `str` | `""` | Seletor de cada item repetido |
| `columns` | `dict` | `None` | Mapeamento nome -> seletor interno |
| `next_page` | `str` | `None` | Seletor do botão "Próxima página" |
| `max_pages` | `int` | `100` | Máximo de páginas a extrair |

### Retorno

Lista de dicts:

```python
[
    {"text": "Citação 1...", "author": "Einstein"},
    {"text": "Citação 2...", "author": "Tolkien"},
]
```

### Exemplo -- Citações

```python
quotes = await browser.extract_data(
    container="body",
    row=".quote",
    columns={
        "text": ".text",
        "author": ".author",
        "tags": ".tags",
    }
)
```

### Exemplo -- Cards de produto

```python
produtos = await browser.extract_data(
    container="#product-list",
    row=".product-card",
    columns={
        "Nome": ".card-title",
        "Preço": ".card-price",
        "Estoque": ".card-stock span",
    },
    next_page="#btn-next",
    max_pages=5,
)
```

### Como descobrir seletores

Use `inspect()` para mapear a estrutura:

```python
# 1. Ver a página geral
await browser.inspect(depth=5)
# Mostra: <div.quote> x 10 items

# 2. Ver dentro de um item
await browser.inspect(".quote", depth=5)
# Mostra: <span.text>, <small.author>, <a.tag>

# 3. Usar no extract_data
data = await browser.extract_data(
    container="body", row=".quote",
    columns={"text": ".text", "author": ".author"}
)
```

---

## extract_table

Extrai dados de uma `<table>` HTML. Usa os cabeçalhos como chaves.

```python
data = await browser.extract_table(selector)
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `selector` | `str` | -- | Seletor da `<table>` |
| `next_page` | `str` | `None` | Seletor do botão próxima página |
| `max_pages` | `int` | `100` | Máximo de páginas |

### Retorno

```python
[
    {"Nome": "João", "CPF": "123.456.789-00", "Saldo": "1.200,00"},
    {"Nome": "Maria", "CPF": "987.654.321-00", "Saldo": "3.500,00"},
]
```

### Exemplo

```python
# Tabela simples
clientes = await browser.extract_table("#clients-table")

# Com paginação
clientes = await browser.extract_table(
    "#clients-table",
    next_page="#btn-next",
    max_pages=10,
)

# Converter para DataFrame
import pandas as pd
df = pd.DataFrame(clientes)
```
