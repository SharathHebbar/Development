import scrapy

class PWCNewsSpider(scrapy.Spider):
    name = "pwc_news1"
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
            "pwc_media1.csv": {"format": "csv"},
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
        # Log page title for debugging
        self.logger.info(f"Scraping URL: {response.url}")
        page_title = response.css("title::text").get(default="").strip()
        self.logger.info(f"Page title: {page_title}")

        # Extract all visible text
        visible_text = response.xpath("//body//text()").getall()
        visible_text = [text.strip() for text in visible_text if text.strip()]

        # Combine visible text into paragraphs
        full_content = " ".join(visible_text)

        # Save to file or yield as output
        yield {
            "Page Title": page_title,
            "Content": full_content,
            "URL": response.url,
        }
