import scrapy
from scrapy_playwright.page import PageMethod

class PWCNewsSpider(scrapy.Spider):
    name = "pwc_news2"
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
        # Log for debugging
        self.logger.info(f"Scraping URL: {response.url}")

        # Loop to click "Load More" button until it disappears
        while True:
            # Extract the entire card (div with class 'collection__item-content')
            
            cards = response.css("div.collection__item-content")

            if not cards:
                self.logger.warning("No cards found on the page.")

            # Loop through each card and extract the required data
            self.logger.info("Cards")
            for card in cards:
                self.logger.info("Inside Cards")
                # heading = card.css("h4.regular.collection__item-heading::text").get(default="").strip()
                heading = card.css("span.ng-binding::text").get(default="").strip()
                paragraph = card.css("p.paragraph.ng-binding::text").get(default="").strip()
                print({
                    "Heading": heading,
                    "Paragraph": paragraph,
                    "URL": response.url,
                })
                if heading not in self.visited_headings:
                    self.visited_headings.add(heading) 
                    yield {
                        "Heading": heading,
                        "Paragraph": paragraph,
                        "URL": response.url,
                    }

            # Check if the "Load more" button is available
            load_more_button = response.css("button.collection__load-more.ng-binding.ng-scope.primary")

            if load_more_button:
                # If the button exists, click it to load more content
                self.logger.info("Clicking 'Load More' button...")
                yield response.follow(
                    url=response.url,
                    callback=self.parse,
                    meta={
                        "playwright": True, 
                        "playwright_actions": [PageMethod("click", "button.collection__load-more.ng-binding.ng-scope.primary")]
                    },
                )
            else:
                # Once the "Load More" button is no longer available, break the loop
                self.logger.info("No 'Load More' button found. All content loaded.")
                break
