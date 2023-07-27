from playwright.async_api import async_playwright

async def get_playwright_browser(headless=False):
    async with async_playwright() as pw:
        # TODO Allow user defined browsers
        browser = await pw.chromium.launch(
            headless=headless
        )
        return browser

    # pw = async_playwright().start()
    # browser = await pw.chromium.launch(
    #     headless=headless
    # )
    # return browser
