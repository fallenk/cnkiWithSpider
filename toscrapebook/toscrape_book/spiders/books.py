# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor  # 解析页面中的链接
from ..items import BookItem  # 导入定义的BookItem类


class BooksSpider(scrapy.Spider):  # 继承scrapy.Spider类
    name = 'books'  # spider名称，为spider唯一标识
    allowed_domains = ['books.toscrape.com']  # 爬取的网页域名
    start_urls = ['http://books.toscrape.com/index.html']  # 爬取起始页

    def parse(self, response):
        # 解析列表页，提取每本书的详情页链接和下一列表页链接
        book_le = LinkExtractor(restrict_css='article.product_pod h3 a')
        book_links = book_le.extract_links(response)
        for book_link in book_links:
            yield scrapy.Request(book_link.url, callback=self.parse_book)  # 详情页Request，调用self.parse_book方法解析

        next_le = LinkExtractor(restrict_css='ul.pager li.next a')
        next_link = next_le.extract_links(response)
        if next_link:
            yield scrapy.Request(next_link[0].url, callback=self.parse)  # 下一列表页Request，调用自身方法解析

    def parse_book(self, response):
        # 解析详情页，提取所需要的数据
        item = BookItem()

        part_one = response.css('div.col-sm-6.product_main')
        item['name'] = part_one.xpath('./h1/text()').extract_first().strip()
        item['price'] = part_one.css('p.price_color::text').extract_first().strip()
        item['rating'] = part_one.css('p.star-rating::attr(class)').re_first('star-rating(.*)').strip()

        part_two = response.css('table.table.table-striped')
        item['upc'] = part_two.xpath('.//tr[1]/td/text()').extract_first().strip()
        item['stock'] = part_two.xpath('.//tr[last()-1]/td/text()').re_first('.*?(\d+).*').strip()
        item['review'] = part_two.xpath('.//tr[last()]/td/text()').extract_first().strip()

        yield item
