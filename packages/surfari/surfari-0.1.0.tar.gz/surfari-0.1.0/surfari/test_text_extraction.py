import surfari_logger

logger = surfari_logger.getLogger(__name__)

from cdp_browser import ChromiumManager
import text_layouter
import asyncio
from playwright.async_api import Locator
from surfari.full_text_extractor import WebPageTextExtractor  
# =============================================================================
# Main Program
# =============================================================================
async def main():
    manager = await ChromiumManager.get_instance(use_system_chrome=False)
    context = manager.browser_context
    page = context.pages[0]
    page.on("console", lambda msg: print(f"Console message: {msg.type}: {msg.text}"))
    # await page.goto("https://www.amazon.com", wait_until="load")
    # await page.goto("https://www.kayak.com/flights", wait_until="load")
    # await page.goto('https://www.amazon.com/s?k=laptop&s=review-rank&crid=1RZCEJ289EUSI&qid=1740202453&sprefix=laptop%2Caps%2C166&ref=sr_st_review-rank&ds=v1%3A4EnYKXVQA7DIE41qCvRZoNB4qN92Jlztd3BPsTFXmxU', wait_until="load")
    await page.goto("https://www.schwab.com/client-home", wait_until="load")
    # await page.goto("https://myedd.edd.ca.gov/s/login/?language=en_US&ec=302&startURL=%2Fs%2F", wait_until="load")            
    # await page.goto("https://www.wellsfargo.com", wait_until="load")
    # await page.goto("https://www.bankofamerica.com", wait_until="load")
    # await page.goto("https://www.google.com/", wait_until="load")
    # await page.goto("https://gmail.google.com/", wait_until="load")            
    # await page.goto("https://www.united.com", wait_until="load")
    # await page.goto("https://www.southwest.com", wait_until="load")            
    # await page.goto("https://www.booking.com/flights", wait_until="load")
    # await page.goto("https://web.oncentrl.com/#/login", wait_until="load")
    # await page.goto("https://www.ally.com", wait_until="load")
    # await page.goto("https://www.expedia.com", wait_until="load")
    # await page.goto("https://calendar.google.com", wait_until="load")
    # await page.goto("https://mail.google.com", wait_until="load")            
    # await page.goto("https://www.linkedin.com/feed/", wait_until="load")
    # await page.goto("https://playwright.dev/python/docs/api/class-locator#locator-evaluate", wait_until="load")
    # await playwright_util.inject_control_bar(page)
    counter = 0
    while counter < 20:  
        counter += 1
        input("Press Enter to continue...")
        await page.wait_for_timeout(3000)
        
        extractor = WebPageTextExtractor()

        full_page_text, legend_dict = await extractor.get_full_text(page, lazy_build_locator=True)
        await logger.log_text_to_file("999", full_page_text, "content")
        legend_str = extractor.filter_legend(legend_dict)
        full_page_text = text_layouter.rearrange_texts(full_page_text, additional_text=legend_str)
        await logger.log_text_to_file("999", full_page_text, "layout")    
        
    logger.info("Page loaded. waiting for browser to be closed manually...")
    await context.wait_for_event("close")

    if ChromiumManager._instance:
        await ChromiumManager._instance.stop()                                  
                            
if __name__ == "__main__":
    asyncio.run(main())
