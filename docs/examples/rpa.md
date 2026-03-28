# Example: RPA Automation

Web portal automation example using PyWebFlx.

## Scenario

Automate login to a portal, extract data from a table, and save it.

## Full code

```python
import asyncio
import pandas as pd
from pywebflx import use_browser, PyWebFlxConfig, configure_logging

configure_logging(level="INFO")

config = PyWebFlxConfig(
    default_timeout=15,
    retry_count=2,
    delay_between_actions=0.5,
)

async def main():
    # 1. Connect to the portal (opens if not already open)
    async with use_browser(
        url="https://portal.example.com",
        config=config,
    ) as browser:

        # 2. Login
        await browser.type_into("#username", text="john@company.com")
        await browser.type_into("#password", text="my-password")
        await browser.click("#btn-login")

        # 3. Wait for dashboard to load
        await browser.wait_element(".dashboard", timeout=10)
        await browser.wait_element_vanish("#spinner")

        # 4. Navigate to reports
        await browser.click(text="Reports", tag="a")
        await browser.wait_element("#clients-table")

        # 5. Extract table
        data = await browser.extract_table(
            "#clients-table",
            next_page="#btn-next",
            max_pages=5,
        )

        # 6. Save to Excel
        df = pd.DataFrame(data)
        df.to_excel("clients.xlsx", index=False)
        print(f"Exported {len(data)} records")

asyncio.run(main())
```

## Multi-tab workflow

```python
async def transfer_data():
    async with use_browser(url="https://portal.com") as portal:
        async with use_browser(url="https://email.com") as email:
            # Extract data from the portal
            balance = await portal.get_text(".account-balance")

            # Paste into email
            await email.click("#new-email")
            await email.type_into("#subject", text="Daily balance")
            await email.type_into("#body", text=f"Balance: {balance}")
            await email.click("#btn-send")
```

## Workflow with error handling

```python
from pywebflx import (
    use_browser,
    ElementNotFoundError,
    BrowserNotFoundError,
    ElementTimeoutError,
)

async def robust_automation():
    try:
        async with use_browser(url="https://portal.com") as browser:

            # Try clicking with retry
            await browser.click(
                "#critical-btn",
                retry=3,
                verify=".success-result",
                timeout=10,
            )

    except BrowserNotFoundError:
        print("Portal is not open")

    except ElementTimeoutError as e:
        print(f"Element {e.selector} did not appear within {e.timeout}s")

    except ElementNotFoundError as e:
        print(f"Element {e.selector} not found")
```

## Workflow with dropdown and checkbox

```python
async def fill_form():
    async with use_browser(url="https://portal.com/register") as browser:
        await browser.type_into("#name", text="John Smith")
        await browser.type_into("#ssn", text="123-45-6789")
        await browser.select_item("#state", "California", by="text")
        await browser.check("#accept-terms")
        await browser.click("#btn-register")
        await browser.wait_element(".success-msg", timeout=10)
```
