from pymongo import MongoClient

# three ways
# client = MongoClient()
# client = MongoClient('localhost', 27017)
# client = MongoClient("http://localhost:27017/")

# 以下两种获取数据库方式
# db = client.pythondb
# db = client['pythondb']
# print(db)

# 以下两种获取集合的方式
# collection = db.python_collection
# collection = db['python-collection']
# print(collection)

import datetime