import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import EurobItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class EurobSpider(scrapy.Spider):
	name = 'eurob'
	start_urls = ['https://www.eurobank.com.cy/en-us/news']

	def parse(self, response):
		articles = response.xpath('//div[@class="ancscard"]')
		for article in articles:
			title = article.xpath('.//h3/text()').get()
			date = article.xpath('.//h4/text()').get()
			post_links = article.xpath('.//a[@class="btn_blue3"]/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date,title=title))

	def parse_post(self, response,date,title):

		content = response.xpath('//div[@class="adetails"]//text()[not (strong[position()>1])]').getall()
		content = [p.strip() for p in content if p.strip()][1:]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=EurobItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
