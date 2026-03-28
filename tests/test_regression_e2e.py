"""
Testes de regressão E2E — PyWebFlx

Roda contra sites reais para garantir que as funcionalidades não quebrem entre deploys.
Requer Chrome aberto com a extensão PyWebFlx instalada.

Sites testados:
  - https://books.toscrape.com/
  - https://webscraper.io/test-sites/tables
  - https://webscraper.io/test-sites/e-commerce/allinone

Executar:
  python -m pytest tests/test_regression_e2e.py -v --timeout=120

Obs: Estes testes abrem abas reais no Chrome. Feche-as após os testes.
"""

import asyncio
import pytest
from pywebflx import use_browser, PyWebFlxConfig

# Timeout generoso para sites externos
CONFIG = PyWebFlxConfig(default_timeout=15)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _connect(url: str):
    """Shortcut: abre a aba e retorna o context manager."""
    return use_browser(url=url, config=CONFIG)


# ===========================================================================
#  SITE 1: books.toscrape.com
# ===========================================================================

class TestBooksToscrape:
    """Testes no catálogo de livros books.toscrape.com."""

    URL = "https://books.toscrape.com/"

    # -- inspect --

    async def test_inspect_returns_structure(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            result = await browser.inspect(depth=3, samples=1)
            assert isinstance(result, str)
            assert len(result) > 50

    async def test_inspect_focused_on_product(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            result = await browser.inspect("article.product_pod", depth=3, samples=1)
            assert isinstance(result, str)
            assert len(result) > 20

    # -- get_text --

    async def test_get_text_book_title(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            title = await browser.get_text("article.product_pod h3 a")
            assert isinstance(title, str)
            assert len(title) > 0

    async def test_get_text_book_price(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            price = await browser.get_text(".product_pod .price_color")
            assert price.startswith("£")

    # -- element_exists --

    async def test_element_exists_positive(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            assert await browser.element_exists("article.product_pod") is True

    async def test_element_exists_negative(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            assert await browser.element_exists("#nonexistent-element-xyz") is False

    # -- extract_data --

    async def test_extract_data_books(self):
        async with use_browser(url=self.URL, open="open", config=CONFIG) as browser:
            await asyncio.sleep(1)
            books = await browser.extract_data(
                container="body",
                row="article.product_pod",
                columns={
                    "title": "h3 a",
                    "price": ".price_color",
                    "availability": ".availability",
                },
            )
            assert isinstance(books, list)
            assert len(books) == 20  # 20 livros por página

            first = books[0]
            assert "title" in first
            assert "price" in first
            assert len(first["title"]) > 0
            assert first["price"].startswith("£")

    async def test_extract_data_columns_match(self):
        """Garante que todas as linhas têm exatamente as colunas pedidas."""
        async with use_browser(url=self.URL, open="open", config=CONFIG) as browser:
            await asyncio.sleep(1)
            books = await browser.extract_data(
                container="body",
                row="article.product_pod",
                columns={"title": "h3 a", "price": ".price_color"},
            )
            for book in books:
                assert set(book.keys()) == {"title", "price"}

    # -- click + navigation --

    async def test_click_next_page(self):
        async with use_browser(url=self.URL, open="open", config=CONFIG) as browser:
            await asyncio.sleep(1)
            # Página 1
            exists = await browser.element_exists("li.next a")
            assert exists is True

            await browser.click("li.next a")
            await asyncio.sleep(1)

            # Verificar que navegou (ainda tem livros)
            exists_after = await browser.element_exists("article.product_pod")
            assert exists_after is True

    async def test_click_book_and_get_detail(self):
        async with use_browser(url=self.URL, open="open", config=CONFIG) as browser:
            await asyncio.sleep(1)
            # Clicar no primeiro livro
            await browser.click("article.product_pod h3 a")
            await asyncio.sleep(1)

            # Deve estar na página de detalhe
            product_name = await browser.get_text("h1")
            assert len(product_name) > 0

            price = await browser.get_text(".price_color")
            assert price.startswith("£")

    # -- get_attribute --

    async def test_get_attribute_href(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            href = await browser.get_attribute("article.product_pod h3 a", attribute="title")
            assert isinstance(href, str)
            assert len(href) > 0

    # -- execute_js --

    async def test_execute_js_document_title(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            title = await browser.execute_js("return document.title")
            assert "books" in title.lower() or "all products" in title.lower()

    # -- get_full_text --

    async def test_get_full_text(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            text = await browser.get_full_text()
            assert isinstance(text, str)
            assert len(text) > 100
            assert "£" in text  # preços devem aparecer


# ===========================================================================
#  SITE 2: webscraper.io/test-sites/tables
# ===========================================================================

class TestWebscraperTables:
    """Testes de extração de tabelas HTML no webscraper.io."""

    URL = "https://webscraper.io/test-sites/tables"

    # -- extract_table --

    async def test_extract_table_basic(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            await asyncio.sleep(1)  # Esperar página carregar completamente
            data = await browser.extract_table("table.table")
            assert isinstance(data, list)
            assert len(data) > 0

            first_row = data[0]
            assert isinstance(first_row, dict)
            assert len(first_row.keys()) >= 2

    async def test_extract_table_has_expected_columns(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            data = await browser.extract_table("table.table")
            if data:
                keys = set(data[0].keys())
                # A tabela de exemplo deve ter colunas como First Name, Last Name, etc.
                assert len(keys) >= 3

    async def test_extract_table_values_not_empty(self):
        """Garante que os valores extraídos não são todos vazios."""
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            data = await browser.extract_table("table.table")
            assert data
            non_empty = sum(1 for row in data for v in row.values() if v.strip())
            assert non_empty > 0

    # -- inspect --

    async def test_inspect_table_structure(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            result = await browser.inspect("table.table", depth=3, samples=1)
            assert isinstance(result, str)
            assert len(result) > 20

    # -- get_text --

    async def test_get_text_table_header(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            header = await browser.get_text("table.table thead th")
            assert isinstance(header, str)
            assert len(header) > 0

    # -- element_exists --

    async def test_table_exists(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            assert await browser.element_exists("table.table") is True

    async def test_tbody_exists(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            assert await browser.element_exists("table.table tbody") is True


# ===========================================================================
#  SITE 3: webscraper.io/test-sites/e-commerce/allinone
# ===========================================================================

class TestWebscraperEcommerce:
    """Testes no e-commerce de exemplo do webscraper.io."""

    URL = "https://webscraper.io/test-sites/e-commerce/allinone"

    # -- inspect --

    async def test_inspect_page(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            result = await browser.inspect(depth=3, samples=1)
            assert isinstance(result, str)
            assert len(result) > 50

    # -- extract_data --

    async def test_extract_data_products(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            products = await browser.extract_data(
                container=".container.test-site",
                row=".col-md-4",
                columns={
                    "title": "a.title",
                    "price": ".price",
                    "description": ".description",
                },
            )
            assert isinstance(products, list)
            assert len(products) > 0

            first = products[0]
            assert "title" in first
            assert "price" in first
            assert "description" in first
            assert len(first["title"]) > 0

    async def test_extract_data_prices_have_dollar(self):
        """Preços devem conter '$'."""
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            products = await browser.extract_data(
                container=".container.test-site",
                row=".col-md-4",
                columns={"price": ".price"},
            )
            assert products
            for p in products:
                assert "$" in p["price"], f"Preço sem '$': {p['price']}"

    # -- get_text --

    async def test_get_text_product_title(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            title = await browser.get_text(".thumbnail a.title")
            assert isinstance(title, str)
            assert len(title) > 0

    async def test_get_text_product_price(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            price = await browser.get_text(".thumbnail .price")
            assert "$" in price

    # -- element_exists --

    async def test_product_cards_exist(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            assert await browser.element_exists(".thumbnail") is True

    # -- click navigation --

    async def test_click_product_and_detail(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            # Clicar no primeiro produto
            await browser.click(".thumbnail a.title")
            await asyncio.sleep(1)

            # Deve carregar página de detalhe
            exists = await browser.element_exists(".caption")
            assert exists is True

    async def test_click_category_navigation(self):
        """Navegar para uma categoria (Computers > Laptops)."""
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            await browser.click(text="Computers", tag="a")
            await asyncio.sleep(2)

            await browser.click(text="Laptops", tag="a")
            await asyncio.sleep(2)

            products = await browser.extract_data(
                container=".container.test-site",
                row=".col-md-4",
                columns={"title": "a.title", "price": ".price"},
            )
            assert len(products) > 0

    # -- get_attribute --

    async def test_get_attribute_product_link(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            href = await browser.get_attribute(".thumbnail a.title", attribute="href")
            assert isinstance(href, str)
            assert len(href) > 0

    # -- execute_js --

    async def test_execute_js_title(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            title = await browser.execute_js("return document.title")
            assert isinstance(title, str)
            assert len(title) > 0

    # -- get_full_text --

    async def test_get_full_text_contains_products(self):
        async with use_browser(url=self.URL, config=CONFIG) as browser:
            text = await browser.get_full_text()
            assert "$" in text  # preços


# ===========================================================================
#  CROSS-SITE: use_browser() behavior
# ===========================================================================

class TestUseBrowserBehavior:
    """Testes do comportamento do use_browser (open, url+title, partial match)."""

    async def test_open_if_not_open_creates_tab(self):
        """open='if_not_open' deve abrir a URL se não existir aba."""
        async with use_browser(
            url="https://books.toscrape.com/",
            open="if_not_open",
            config=CONFIG,
        ) as browser:
            title = await browser.execute_js("return document.title")
            assert "books" in title.lower() or "all products" in title.lower()

    async def test_open_always_opens_new_tab(self):
        """open='open' deve sempre abrir nova aba."""
        async with use_browser(
            url="https://books.toscrape.com/",
            open="open",
            config=CONFIG,
        ) as browser:
            exists = await browser.element_exists("article.product_pod")
            assert exists is True

    async def test_partial_url_match(self):
        """URL parcial deve encontrar a aba já aberta."""
        # Primeiro abre a aba
        async with use_browser(
            url="https://books.toscrape.com/",
            open="open",
            config=CONFIG,
        ) as _:
            pass

        await asyncio.sleep(1)

        # Agora busca com URL parcial
        async with use_browser(
            url="books.toscrape.com",
            open="never",
            config=CONFIG,
        ) as browser:
            exists = await browser.element_exists("article.product_pod")
            assert exists is True

    async def test_url_and_title_combined(self):
        """Usar url + title juntos (lógica AND)."""
        # Abrir a aba primeiro
        async with use_browser(
            url="https://books.toscrape.com/",
            open="open",
            config=CONFIG,
        ) as _:
            pass

        await asyncio.sleep(1)

        # Buscar com url + title
        async with use_browser(
            url="books.toscrape",
            title="All products",
            open="never",
            config=CONFIG,
        ) as browser:
            price = await browser.get_text(".price_color")
            assert price.startswith("£")


# ===========================================================================
#  Sync runner (para rodar com pytest sem plugin asyncio)
# ===========================================================================

def _run(coro):
    """Roda coroutine no event loop."""
    return asyncio.run(coro)


# Gerar métodos sync para cada teste async
def _make_sync_tests():
    """Converte todos os testes async em funções sync para pytest."""
    import sys
    module = sys.modules[__name__]

    for cls in [
        TestBooksToscrape,
        TestWebscraperTables,
        TestWebscraperEcommerce,
        TestUseBrowserBehavior,
    ]:
        for name in list(vars(cls)):
            if name.startswith("test_") and asyncio.iscoroutinefunction(getattr(cls, name)):
                method = getattr(cls, name)

                def make_sync(m):
                    def sync_test(self):
                        _run(m(self))
                    sync_test.__name__ = m.__name__
                    sync_test.__doc__ = m.__doc__
                    return sync_test

                setattr(cls, name, make_sync(method))


_make_sync_tests()
