# Navegacao

Metodos para navegar entre paginas, atualizar e fechar abas.

---

## navigate_to

Navega para uma URL na aba atual.

```python
await browser.navigate_to("https://portal.example.com/dashboard")
```

---

## go_back

Volta no historico do navegador.

```python
await browser.go_back()
```

---

## go_forward

Avanca no historico do navegador.

```python
await browser.go_forward()
```

---

## refresh

Recarrega a pagina atual.

```python
await browser.refresh()
```

---

## close_tab

Fecha a aba atual.

```python
await browser.close_tab()
```

---

## close_browser

Fecha o navegador (todas as abas).

```python
await browser.close_browser()
```
