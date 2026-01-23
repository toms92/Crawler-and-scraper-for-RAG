from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class UrlSpider(CrawlSpider):

    name = "primo_spyder"
    allowed_domains = ["giallozafferano.it"]
    start_urls = ["https://www.giallozafferano.it/ricette-cat/"]

    custom_settins = {
        'CLOSESPIDER_PAGECOUNT': 10,
    }

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        for link in response.css('h2.gz-title a::attr(href)').getall():
            yield {
                'url': response.urljoin(link)  # Trasforma link relativi in assoluti
            }
        yield {
            'url': response.url
        }
        prossima_pagina = response.css('a.gz-arrow.next::attr(href)').get()
        if prossima_pagina:
            yield response.follow(prossima_pagina, callback=self.parse)
