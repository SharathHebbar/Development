import scrapy


class EYNewsSpider(scrapy.Spider):
    name = "ey_news"
    allowed_domains = ["ey.com"]
    start_urls = ["https://www.ey.com/en_au/newsroom#tabs-a631bd6331-item-f3ab1b019e-tab"]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "ROBOTSTXT_OBEY": True,
        "FEEDS": {
            "ey_news.csv": {"format": "csv"},
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

        # Parse the news items
        articles = response.css("div.teaser__content")

        if not articles:
            self.logger.warning("No articles found on the page.")

        for article in articles:
            heading = article.css("h3.teaser__title::text").get(default="").strip()
            content = article.css("p.teaser__summary::text").get(default="").strip()
            relative_url = article.css("a.teaser__link::attr(href)").get()
            url = response.urljoin(relative_url) if relative_url else None

            yield {
                "Heading": heading,
                "Content": content,
                "URL": url,
            }

        # Handle pagination
        next_page = response.css("a.pagination__link--next::attr(href)").get()
        if next_page:
            self.logger.info(f"Following pagination to {next_page}")
            yield response.follow(
                next_page,
                meta={"playwright": True},
                callback=self.parse,
            )
