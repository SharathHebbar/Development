import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.exceptions import CloseSpider
import time

class PWCNewsSpider(scrapy.Spider):
    name = "pwc_news4"
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
        self.visited_headings = set()  # Set to keep track of unique headings
        self.max_retries = 5  # Maximum number of retries for clicking 'Load More'

    def start_requests(self):
        """
        Initialize the scraping process by sending requests to the start URLs.
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},
            )

    async def parse(self, response):
        """
        Parse the main page and extract the necessary card content.
        Also click the 'Load More' button to load additional cards dynamically.
        """
        # Log for debugging
        self.logger.info(f"Scraping URL: {response.url}")

        # Extract cards from the page
        cards = response.css("div.collection__item-content")

        if not cards:
            self.logger.warning("No cards found on the page.")

        # Loop through each card and extract the required data
        for card in cards:
            heading = card.css("span.ng-binding::text").get(default="").strip()
            paragraph = card.css("p.paragraph.ng-binding::text").get(default="").strip()

            # Only yield data if the heading is unique (not seen before)
            if heading not in self.visited_headings:
                self.visited_headings.add(heading)  # Mark this heading as visited
                yield {
                    "Heading": heading,
                    "Paragraph": paragraph,
                    "URL": response.url,
                }

        # Try clicking the "Load More" button and loading additional content
        retries = 0
        while retries < self.max_retries:
            try:
                # load_more_button = response.css("btn.btn--transparent.collection__load-more.ng-binding.ng-scope.primary")
                load_more_button = response.css("button.btn--transparent.collection__load-more")
                if load_more_button:
                    self.logger.info("Clicking 'Load More' button...")
                    # Simulate clicking 'Load More' and wait for the new content to load
                    yield response.follow(
                        url=response.url,
                        callback=self.parse,
                        meta={
                            "playwright": True, 
                            "playwright_actions": [
                                # PageMethod("click", "btn.btn--transparent.collection__load-more.ng-binding.ng-scope.primary")
                                PageMethod("click", "button.btn--transparent.collection__load-more")
                            ]
                        },
                    )
                    # Wait for the new content to load
                    time.sleep(2)  # Adjust as needed to give time for content to load
                    return  # Return to prevent further processing while waiting for more content
                else:
                    self.logger.info("No 'Load More' button found or button is disabled.")
                    break  # Exit the loop if the 'Load More' button is no longer available or enabled
            except Exception as e:
                retries += 1
                self.logger.error(f"Error clicking 'Load More': {e}. Retrying {retries}/{self.max_retries}...")
                if retries >= self.max_retries:
                    self.logger.warning("Max retries reached. Stopping 'Load More' attempts.")
                    break
                time.sleep(2)  # Wait before retrying

        # If the button is no longer available, end the scraping process
        if retries >= self.max_retries:
            self.logger.info("Max retries reached. Exiting spider.")
            raise CloseSpider("Max retries reached for 'Load More' button.")
