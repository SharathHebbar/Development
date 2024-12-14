import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.exceptions import CloseSpider
import time

class PWCNewsSpider(scrapy.Spider):
    name = "pwc_news7"
    allowed_domains = ["pwc.com.au"]
    start_urls = ["https://www.pwc.com.au/media.html"]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "ROBOTSTXT_OBEY": True,
        "FEEDS": {
            "pwc_cards.csv": {"format": "csv"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }

    def __init__(self, *args, **kwargs):
        super(PWCNewsSpider, self).__init__(*args, **kwargs)
        self.visited_headings = set()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},
            )

    async def parse(self, response):
        self.logger.info(f"Scraping URL: {response.url}")

        # Extract cards from the page
        cards = response.css("div.collection__item-content")
        if not cards:
            self.logger.warning("No cards found on the page.")
        
        # Loop through each card and extract the required data
        for card in cards:
            heading = card.css("span.ng-binding::text").get(default="").strip()
            paragraph = card.css("p.paragraph.ng-binding::text").get(default="").strip()

            # Only yield data if the heading is unique
            if heading not in self.visited_headings:
                self.visited_headings.add(heading)
                yield {
                    "Heading": heading,
                    "Paragraph": paragraph,
                    "URL": response.url,
                }

        # Wait for the 'Load More' button and click it
        load_more_button = response.css("button.btn--transparent.collection__load-more")
        if load_more_button:
            self.logger.info("Clicking 'Load More' button...")
            
            # Wait for the button to be enabled
            page = response.meta["playwright_page"]
            await page.wait_for_selector("button.btn--transparent.collection__load-more:enabled")
            
            # Click the button
            yield response.follow(
                url=response.url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_actions": [PageMethod("click", "button.btn--transparent.collection__load-more")]
                },
            )
            time.sleep(2)  # Ensure there's enough time for the page to load
        else:
            self.logger.info("No more 'Load More' button found. Ending scraping.")
            raise CloseSpider("No more 'Load More' button found.")
