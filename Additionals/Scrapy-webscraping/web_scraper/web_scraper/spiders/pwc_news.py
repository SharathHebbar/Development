import scrapy

class PWCNewsSpider(scrapy.Spider):
    name = "pwc_news"
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

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},
            )

    def parse(self, response):
        # Log for debugging
        self.logger.info(f"Scraping URL: {response.url}")

        # Extract the entire card (div with class 'collection__item-content')
        cards = response.css("div.collection__item-content")

        if not cards:
            self.logger.warning("No cards found on the page.")

        # Loop through each card and extract the required data
        for card in cards:
            heading = card.css("h4.regular.collection__item-heading::text").get(default="").strip()
            paragraph = card.css("p.paragraph.ng-binding::text").get(default="").strip()

            yield {
                "Heading": heading,
                "Paragraph": paragraph,
                "URL": response.url,
            }
