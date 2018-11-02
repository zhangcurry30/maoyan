# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


#电影“影”的影院信息
class MaoyanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    #影院所在地
    city = scrapy.Field()
    # 影院链接
    href = scrapy.Field()
    # 影院名称
    title = scrapy.Field()
    # 影院位置
    location = scrapy.Field()

#影厅信息
class moviehallItem(scrapy.Item):

    # 影厅所在地
    city = scrapy.Field()
    # 放映厅名称
    title = scrapy.Field()
    #放映时间
    time = scrapy.Field()
    #语言版本
    language = scrapy.Field()
    #影票售价
    price = scrapy.Field()
    #影厅选座链接
    href = scrapy.Field()

#影厅选座情况
class seatNumItem(scrapy.Item):
    #座位信息
    seat = scrapy.Field()
    #价格
    price = scrapy.Field()

