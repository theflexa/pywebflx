# inspect

Retorna uma visao resumida da estrutura do DOM, otimizada para consumo por IA e depuracao rapida.

Usa **~95% menos tokens** que o HTML bruto, preservando informacoes uteis.

## Assinatura

```python
structure = await browser.inspect(selector="", depth=2, samples=2)
```

## Parametros

| Parametro | Tipo | Padrao | Descricao |
|-----------|------|--------|-----------|
| `selector` | `str` | `""` | Escopo (vazio = pagina inteira) |
| `depth` | `int` | `2` | Profundidade maxima de travessia |
| `samples` | `int` | `2` | Amostras de dados em listas/tabelas |

## Exemplo de saida

```
<body>
  <header#top-nav .navbar>
    <button.btn-menu> "Menu"
    <input#search type="search" placeholder="Buscar...">
    <a.logo> "Portal Sicoob"
  <main#content>
    <form#login-form>
      <input#username type="text" placeholder="Usuario" [required]>
      <input#password type="password" placeholder="Senha" [required]>
      <select#branch> 3 opcoes: ["0001 - Centro", "0032 - Belem"]
      <button#btn-login type="submit"> "Entrar"
    <div.notices>
      <table#notices-table> 3 cols x 12 linhas
        cabecalhos: ["Data", "Tipo", "Mensagem"]
        amostra[0]: ["28/03", "Info", "Manutencao programada"]
```

## Fluxo de uso

### 1. Inspect geral -- entender a pagina

```python
structure = await browser.inspect(depth=5, samples=2)
print(structure)
```

Resultado:
```
<div.quote> x 10 items
  sample[0]: "The world as we have created it..."
```

### 2. Inspect focado -- ver dentro de um elemento

```python
detail = await browser.inspect(".quote", depth=5)
print(detail)
```

Resultado:
```
<div.quote>
  <span.text> "The world as we have created it..."
  <span>
    <small.author> "Albert Einstein"
  <div.tags>
    <a.tag> x 3 items
      sample[0]: "change"
```

### 3. Usar os seletores descobertos

```python
quotes = await browser.extract_data(
    container="body",
    row=".quote",
    columns={"text": ".text", "author": ".author"}
)
```

## O que o inspect mostra

| Elemento | Como aparece |
|----------|-------------|
| IDs e classes | `<div#login-form.container>` |
| Inputs | `<input#email type="text" placeholder="Email" [required]>` |
| Links | `<a.logo href="/home">` |
| Texto | `<button> "Entrar"` |
| Tabelas | `<table> 3 cols x 12 linhas` + cabecalhos + amostras |
| Selects | `<select> 5 opcoes: ["Opt1", "Opt2", ...]` |
| Listas | `<div.card> x 20 items` + amostras |

## Quando usar

| Cenario | Comando |
|---------|---------|
| Entender uma pagina desconhecida | `inspect(depth=5)` |
| Encontrar seletores para automacao | `inspect(".container", depth=5)` |
| Alimentar IA com contexto da pagina | `inspect(depth=3, samples=2)` |
| Depuracao rapida sem DevTools | `inspect()` |
