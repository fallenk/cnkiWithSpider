# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()  # 书名
    price = scrapy.Field()  # 价格，以欧元计
    rating = scrapy.Field()  # 评分，为’One‘、’Two‘、’Three‘、’Four‘、’Five‘
    upc = scrapy.Field()  # upc
    stock = scrapy.Field()  # 库存
    review = scrapy.Field()  # 评价数
