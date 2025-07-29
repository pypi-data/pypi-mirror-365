
# Playwright version of apply_filter
import asyncio
from playwright.async_api import Page

async def apply_filter(page: Page, event_location: str, event_name: str):
    try:
        # Click the filter dropdown for location
        all_filter_fields = await page.query_selector_all("//span[contains(@class, 'filter-name')]")
        await all_filter_fields[0].click()

        # Input location search text
        filter_inputs = await page.query_selector_all("//input[contains(@class, 'search-text')]")
        await filter_inputs[1].fill(event_location)

        # Select the checkbox for the location
        location_label = await page.wait_for_selector(f"//label[@class='filters-checkbox' and contains(., '{event_location}')]")
        await location_label.click()

        # Click the filter dropdown for event name
        await asyncio.sleep(1)
        await all_filter_fields[1].click()

        await filter_inputs[2].fill(event_name)

        name_label = await page.wait_for_selector(f"//label[@class='filters-checkbox' and contains(., '{event_name}')]")
        await name_label.click()

        # Find session listings using CSS selectors
        await asyncio.sleep(1)
        await asyncio.gather(
            page.wait_for_load_state('load'),  # Full page load
            page.wait_for_selector("table.bm-classes-grid tr")  # Element availability
        )

        print("Successfully applied filter")
    except Exception as e:
        print("Could not apply filter:", e)
        raise


# Example usage for testing
if __name__ == "__main__":
    import sys
    from playwright.async_api import async_playwright

    async def main():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto("https://vaughan.perfectmind.com/25076/Clients/BookMe4BookingPages/Classes?calendarId=1d032376-c4bb-4023-80f5-7c3c44de0637&widgetId=dff88c8a-0b78-4a94-9dde-250040385300&embed=False")
            await apply_filter(page, 'Vellore Village Community Centre', 'Volleyball')
            await asyncio.sleep(5)
            await browser.close()

    asyncio.run(main())