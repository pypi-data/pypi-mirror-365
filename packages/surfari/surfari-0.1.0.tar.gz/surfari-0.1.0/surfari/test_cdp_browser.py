
import asyncio
from cdp_browser import ChromiumManager

import surfari_logger
logger = surfari_logger.getLogger(__name__)

async def main():
    """
    1) System Chrome usage:
       - use_system_chrome=True
    2) Bundled Chromium usage:
       - use_system_chrome=False
    """
    # manager = ChromiumManager(use_system_chrome=True)
    # manager = ChromiumManager(remote_debugging_port=9222)

    manager = await ChromiumManager.get_instance(use_system_chrome=True)

    # Access the BrowserContext and open a new tab
    page = await manager.get_new_page()
    context = manager.browser_context  # still accessible

    # await page.goto("https://www.citi.com/")
    # await page.goto("https://us.etrade.com/home/welcome-back")
    # await page.goto("https://deviceandbrowserinfo.com/info_device")
    # await page.goto("https://bot.sannysoft.com/")
    await page.goto("https://bot-detector.rebrowser.net/")
    # await page.goto("https://www.webflow.com/")
    # await page.goto("https://www.okta.com/")
    # await page.goto("https://abrahamjuliot.github.io/creepjs/")
    # await page.goto("https://nowsecure.nl/")

    logger.info("Page loaded. waiting for browser to be closed manually...")
    await context.wait_for_event("close")

    if ChromiumManager._instance:
        await ChromiumManager._instance.stop()
        
if __name__ == "__main__":
    asyncio.run(main())