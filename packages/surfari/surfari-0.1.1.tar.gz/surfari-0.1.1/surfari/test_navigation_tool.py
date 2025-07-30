from surfari.cdp_browser import ChromiumManager
from surfari_logger import getLogger
from tools.navigation_tool import NavigationTool
import asyncio

logger = getLogger(__name__)

TEST_CASES = {
    1: ("cricket", "Download my March-April 2025 statements."),
    2: ("schwab", "From my main account, purchase 120 shares of AAPL, $125.00 limit, good till cancel until 10/20, reinvest dividends"),    
    3: ("etrade", "Move $7.99 from my brokerage account to checking account on July 10."),
    4: ("united", "Using expedia to Find tickets from San Francisco to Atlanta, two adult passengers and one 14 years old, one 1 year old infant with seat, leaving on July 22, 2025, returning on July 29, direct flight or at most 1 stop, price under $500 per person."),
    5: ("calendar", "Use my google account. Create a 3 hour google calendar meeting for Redwoods Lodging with xiaojun, on July 7, 12:00 PM PT. Add google meeting. Send invite."),
    6: ("google", "Use ally bank to transfer $6.20 to my bank of america account from joint savings, on the last business day of every month, starting in June, until 10/20/2025. Find its url if needed."),
    7: ("amazon", "Check the details of Orange PI 5 under $150. What CPU and GPU does it have. Don't buy it."),
    8: ("wells fargo", "Zelle $1000.00 to hgsb from my checking account for 'Love offerings: Brother Eric Wu, $250, Brother Alex Pin $250, Building Fund $500'."),
    9: ("venmo", "Send 1.39 for Lunch Bill Split to @Eric-Zhang-117."),
    10: ("myhealthonline", "What was the test result of my last Mammograph done, when was it done, where was it done?"),
    11: ("labcorp", "Download my last lab report. What was my blood glucose level? Download the report."),
    12: ("bankofamerica", "How much did we pay my insurance company (CONNECT BY AMFAM) last time for home and auto using credit card in 2024?"),
    13: ("pge", "Download my April 2025 statement"),
    14: ("benefit", "How much money do I have in what account?"),
    15: ("via benefits", "How much money do I have in all my accounts?"),
    16: ("edd", "Login and Certify my unemployment for all available weeks. Answer all questions with No except that I am looking for work. And check federal tax withholding. My zip code is 95014. Don't submit the form."),
    17: ("schwab", "Show me how to create a limit order for 3 shares of TSLA at $210.99, good till cancel. Don't place the order."),
    18: ("xfinity", "Download my April 2025 and May 2025 statements."),
    19: ("centrl", "Login to https://web.oncentrl.com/#/login and go to R360 partner space. Respond to assessment ILPA with realistic dummy data. Answer yes to yes/no answers. For follow-up questions like 1.8 → 1.8.1, answer accordingly. Complete each section before saving and moving on. Don't submit."),
    20: ("gmail", "Use my gmail account. Send an email to Eric and tell him we are arriving at 10 pm in Boston next Tuesday."),
    21: ("PANW", "why was Palo Alto Networks stock down more than 5% today, double check it is today, any news if not reporting earnings?"),
    22: ("linkedin", "Look at my own linkedin profile and find CTO job opportunities that match my profile, 100–200 people company."),
    23: ("schwab", "From my main account, cancel AAPL order "),
}

async def test_navigation_tool():
    test_case = 4  # Change this to run a different test case
    if test_case not in TEST_CASES:
        logger.error(f"Invalid test_case: {test_case}")
        return

    site_name, task_goal = TEST_CASES[test_case]
    logger.info(f"Running test case {test_case}: {site_name} → {task_goal}")

    manager = await ChromiumManager.get_instance(use_system_chrome=False)
    context = manager.browser_context
    page = context.pages[0]

    nav_tool = NavigationTool(site_name=site_name, mask_sensitive_info=False)
    answer = await nav_tool.navigate(page, task_goal=task_goal)
    print("Final answer:", answer)

if __name__ == "__main__":
    asyncio.run(test_navigation_tool())
