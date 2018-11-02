# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from maoyanMovie.items import seatNumItem
import pymysql
from maoyanMovie import settings
from logging import log

class MaoyanmoviePipeline(object):
    def process_item(self, item, spider):
        return item

class DBpipeline():
    def __init__(self):
        # 连接数据库
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)

        # 通过cursor执行增删查改

        self.cursor = self.connect.cursor()
    def process_item(self, item, spider):
        try:
             # 插入数据
            self.cursor.execute(
                """insert into cinemas(city, time, language, title, href)
                value (%s, %s, %s, %s, %s)""",
                (item['city'], item['time'], item['language'], item['title'], item['href']))

            # 提交sql语句
            self.connect.commit()

        except Exception as error:
            # 出现错误时打印错误日志
            log(error)
        return item



