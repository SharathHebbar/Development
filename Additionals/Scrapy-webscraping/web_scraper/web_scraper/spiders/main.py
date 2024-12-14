import scrapy


class AtoNewsSpider(scrapy.Spider):
    name = "ato_news"
    allowed_domains = [
        "ato.gov.au", 
        "pwc.com.au",
        "ey.com"

    ]
    start_urls = [
        "https://www.ato.gov.au/whats-new#sortCriteria=%40dateupdated%20descending",
        "https://www.pwc.com.au/media.html",
        "https://www.ey.com/en_au/newsroom",
    ]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 2,
        "FEED_FORMAT": 'csv',
        "FEED_URI": 'output.csv'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                },
                meta={
                    "playwright": True,
                    "playwright_context": "default",
                    "playwright_page_methods": [
                        {
                            "method": "wait_for_selector",
                            "args": ["div.AtoSearchResultsItem_result-item__DBedq"],
                        }
                    ],
                },
            )


    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield scrapy.Request(
    #             url,
    #             meta={
    #                 "playwright": True,
    #                 "playwright_context": "default",
    #                 "playwright_page_methods": [
    #                     {
    #                         "method": "wait_for_selector",
    #                         "args": ["div.AtoSearchResultsItem_result-item__DBedq"],
    #                     }
    #                 ],
    #             },
    #         )

    async def parse(self, response):
        # Extract the dynamically loaded content
        self.logger.info(f"Scraping: {response.url}")
        news_items = response.css("div.AtoSearchResultsItem_result-item__DBedq")

        for item in news_items:
            headline = item.css("h2::text").get(default="").strip()
            summary = item.css("p::text").get(default="").strip()
            published_on = item.css("div::text").get(default="").strip()
            anchor = item.css("a::attr(href)").get(default="")
            full_url = response.urljoin(anchor)

            yield {
                "headline": headline,
                "summary": summary,
                "published_on": published_on,
                "url": full_url,
            }

        # Pagination logic
        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                meta={"playwright": True},
                callback=self.parse,
            )