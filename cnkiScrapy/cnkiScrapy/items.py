# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CnkiscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    title = scrapy.Field()
    detailLink = scrapy.Field()
    author = scrapy.Field()
    source = scrapy.Field()
    publicationDate = scrapy.Field()
    dateBase = scrapy.Field()
    referenceNum = scrapy.Field()
    downloadNum = scrapy.Field()
    pdfDownLink = scrapy.Field()

class CnkidetailItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    referenceTitle = scrapy.Field()
    viceTitle = scrapy.Field()
    introDetail = scrapy.Field()
    date = scrapy.Field()
    version = scrapy.Field()
    classNum = scrapy.Field()
