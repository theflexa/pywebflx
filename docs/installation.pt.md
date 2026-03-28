# Instalacao

## 1. Instalar a biblioteca

```bash
pip install pywebflx
```

Ou para desenvolvimento:

```bash
git clone https://github.com/theflexa/pywebflx.git
cd pywebflx
pip install -e ".[dev]"
```

## 2. Instalar a extensao do Chrome

### Via CLI

```bash
pywebflx install-extension
```

O comando exibe o caminho da pasta `extension/` e abre `chrome://extensions`.

### Manual

1. Abra `chrome://extensions` no Chrome
2. Ative o **Modo do desenvolvedor** (canto superior direito)
3. Clique em **Carregar sem compactacao**
4. Selecione a pasta `extension/` do projeto
5. A extensao **PyWebFlx Bridge** deve aparecer

## 3. Verificar

```bash
pywebflx check
```

Se aparecer "Extension is CONNECTED!", tudo esta pronto.

## Requisitos

- Python 3.10+
- Google Chrome
- Extensao PyWebFlx Bridge instalada

## Dependencias

| Pacote | Uso |
|--------|-----|
| `websockets` | Comunicacao Python <-> Extensao |
| `loguru` | Logging estruturado |
| `click` | CLI (install-extension, check) |
