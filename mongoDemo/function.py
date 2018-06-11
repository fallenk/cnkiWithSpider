import os
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)
# db
db = client.test
# collection
txt_set = db.xi  # 使用test_set集合，没有则自动创建
key_set = db.xi_key

key_one = ["平安浙江", "社会管理", "党的领导", "共建", "共治", "共享", "综合治理", "系统治理", "基层", "法治"]
key_two = ["党建", "基层党建", "作风建设", "公民参与", "社会组织", "群众参与", "维权", "共同参与",
           "平安", "社会建设", "治安", "综合", "维稳", "稳定", "信访", "社会矛盾", "依法管理",
           "系统管理", "综合管理", "法治", "法治保障", "枫桥", "枫桥经验"]
key_three = ["腐败", "队伍", "群众", "扶贫", "食品", "生产", "依法治理", "系统", "依法", "综合",
             "源头", "社会", "矛盾", "参与"]


# fun_1: 给到一个关键词，获得它首次出现的文章信息
def fun_1(key_value):
    '''
    fun_1: 给到一个关键词，获得它首次出现的文章信息
    :param key_value: 
    :return
    '''
    records = txt_set.find({"content": {'$regex': key_value}}).sort("publicDate").limit(1)
    for rec in records:
        print("keyword:" + key_value)
        # print("_id:", rec["_id"])
        # TODO some problems without title
        # print("title: " + str(rec["title"]) + "\tDate: " + str(rec["publicDate"]))
        print("_id: " + str(rec["_id"]))


# fun_2: 给到一个关键词， 给出它出现文章次数， 按年份给出文章数
def fun_2(key_value):
    total_records = txt_set.find({"content": {'$regex': key_value}})
    year_records = []
    for i in range(2002, 2008):
        start = str(i) + "-01-01"
        end = str(i + 1) + "-01-01"
        recs = txt_set.find({"content": {'$regex': key_value}, "publicDate": {'$gte': start, '$lt': end}})
        print("year:" + str(i) + "\tnum:" + str(recs.count()))
        for rec in recs:
            print("title: " + str(rec["title"]) + "\tDate: " + str(rec["publicDate"]))
        year_records.append(recs.count())


# fun_3: 给任意两个关键词，给出同时两个关键词的文章
def fun_3(key1, key2):
    records = txt_set.find({"content": {'$regex': key1, '$regex': key2}}).sort("publicDate")
    print("keyword:" + key1 + "\t" + key2)
    print("txt_num:" + str(records.count()))
    for rec in records:
        print("title: " + str(rec["title"]) + "\tDate: " + str(rec["publicDate"]))
    return int(records.count())


# fun_4: 给一个关键词，找出和它关系最近的词
def takeSecond(elem):
    return elem[1]


def fun_4(key_value):
    keys = []
    keys.extend(key_one)
    keys.extend(key_two)
    keys.extend(key_three)
	
    key_list = []
    for key in keys:
        if key == key_value:
            continue
        records = txt_set.find({"content": {'$regex': key_value, '$regex': key}}).sort("publicDate")
        txt_num = records.count()
        key_list.append((key, txt_num))
    key_list.sort(key=takeSecond, reverse=True)
    print(key_list)


if __name__ == "__main__":
    fun_1(key_one[1])
    # fun_2(key_one[0])
    # _ = fun_3(key_one[0], key_one[1])
    # fun_4(key_one[0])
