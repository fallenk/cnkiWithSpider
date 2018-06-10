# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo  # 用于将解析的数据存入MongoDB
from scrapy.item import Item  # 导入Item类
import sqlite3
from twisted.enterprise import adbapi
import pymysql
import redis


class BookPipeline(object):
    # 将原始数据中评分转换为阿拉伯数字表示，价格由欧元转换为人民币表示
    rating_map = {  # 评分中英文单词与阿拉伯数字的对应关系
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5,
    }
    price_rate = 7.7911  # 价格中欧元与人民币的兑换汇率

    def process_item(self, item, spider):
        origin_rating = item.get('rating')  # 原始数据中的评分
        origin_price = float(item.get('price')[1:])  # 原始数据中的价格，转换为float类型
        if origin_rating:
            item['rating'] = self.rating_map[origin_rating]  # 将评分转换为阿拉伯数字表示
        if origin_price:
            item['price'] = '￥%.2f' % (origin_price*self.price_rate)  # 将价格转换为人民币表示
        return item


class MongoPipeline(object):
    #  将数据存入MongoDB数据库中
    @classmethod
    def from_crawler(cls, crawler):
        # 类方法，读取settings.py中的配置，根据配置创建MongoPipeline对象
        cls.MONGO_CLIENT = crawler.settings.get('MONGO_CLIENT', 'mongodb://localhost:27017/')
        cls.MONGO_DB = crawler.settings.get('MONGO_DB', 'toscrape_book')
        return cls()

    def open_spider(self, spider):
        # 创建MongoDB连接，指明连接的数据库和集合
        self.client = pymongo.MongoClient(self.MONGO_CLIENT)
        self.db = self.client[self.MONGO_DB]
        self.collection = self.db[spider.name]  # 集合名为spider.name

    def close_spider(self, spider):
        # 数据处理完后，关闭MongoDB连接
        self.client.close()

    def process_item(self, item, spider):
        # 将数据存入MongoDB集合中
        if isinstance(item, Item):  # 传入的item为Item类型，先转换为dict类型再存入MongoDB
            db_item = dict(item)
        else:
            db_item = item
        self.collection.insert_one(db_item)
        return item


class SQLitePipeline(object):

    def open_spider(self, spider):
        db_name = spider.settings.get('SQLITE_DB', 'scrapy.db')
        self.db_conn = sqlite3.connect(db_name)
        self.db_cur = self.db_conn.cursor()

    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        values = (
            item['upc'],
            item['name'],
            item['price'],
            item['rating'],
            item['stock'],
            item['review']
        )
        sql = 'insert into books values(?,?,?,?,?,?)'
        self.db_cur.execute(sql, values)


class MySQLAsyncPipeline(object):

    def open_spider(self, spider):
        host = spider.settings.get('MYSQL_HOST', 'localhost')
        port = spider.settings.get('MYSQL_PORT', 3306)
        db = spider.settings.get('MYSQL_DB', 'scrapy_db')
        user = spider.settings.get('MYSQL_USER', 'root')
        passwd = spider.settings.get('MYSQL_PASSWORD', '123456')
        charset = spider.settings.get('MYSQL_CHARSET', 'utf8')
        self.dbpool = adbapi.ConnectionPool('pymysql', host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)

    def close_spider(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        self.dbpool.runInteraction(self.insert_db, item)
        return item

    def insert_db(self, tx, item):
        values = (
            item['upc'],
            item['name'],
            item['price'],
            item['rating'],
            item['stock'],
            item['review']
        )
        sql = 'insert into books values(%s,%s,%s,%s,%s,%s)'
        tx.execute(sql, values)


class MySQLPipeline(object):

    def open_spider(self, spider):
        host = spider.settings.get('MYSQL_HOST', 'localhost')
        port = spider.settings.get('MYSQL_PORT', 3306)
        db = spider.settings.get('MYSQL_DB', 'scrapy_db')
        user = spider.settings.get('MYSQL_USER', 'root')
        passwd = spider.settings.get('MYSQL_PASSWORD', '123456')
        charset = spider.settings.get('MYSQL_CHARSET', 'utf8')
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        values = (
            item['upc'],
            item['name'],
            item['price'],
            item['rating'],
            item['stock'],
            item['review']
        )
        sql = 'insert into books1 values(%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(sql, values)


class RedisPipeline(object):

    def open_spider(self, spider):
        host = spider.settings.get('REDIS_HOST', 'localhost')
        port = spider.settings.get('REDIS_PORT', 6379)
        db = spider.settings.get('REDIS_DB', 0)
        self.conn = redis.StrictRedis(host=host, port=port, db=db)
        self.item_i = 1

    def close_spider(self, spider):
        self.conn.connection_pool.disconnect()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        if isinstance(item, Item):
            item = dict(item)
        self.conn.hmset('book:%s' % self.item_i, item)
        self.item_i += 1
