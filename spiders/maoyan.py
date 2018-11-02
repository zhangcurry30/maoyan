# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from maoyanMovie.items import MaoyanItem, moviehallItem, seatNumItem
from maoyanMovie.cookies import cookies
from maoyanMovie.proxy import get_proxy
from scrapy.selector import Selector

class MaoyanSpider(scrapy.Spider):
    name = 'maoyan'
    allowed_domains = ['www.maoyan.com']
    start_urls = ['http://maoyan.com/cinemas?movieId=342062',
                 'http://ip.filefab.com/index.php']

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/58.0.3029.110 Safari/537.36"}


    def start_requests(self):
        #构造每一个城市的cookie
        for i in range(0, 3):
            yield Request(url=self.start_urls[0], callback=self.parse_cookie, headers=self.headers, cookies=cookies[i],
                    dont_filter='true', encoding='utf-8', meta={'cookie': cookies[i]})#, 'proxy': 'http://'+get_proxy()})

    #判断状态码
    def proxy(self, response):
        cookie = response.meta['cookie']
        if response.status == 200:
            yield Request(url=self.start_urls[0], callback=self.parse_cookie, headers=self.headers, cookies=cookie,
                    dont_filter='true', encoding='utf-8', meta={'cookie': cookie})
        elif response.status == 403:
            yield Request(url=self.start_urls[0], callback=self.parse_cookie, headers=self.headers, cookies=cookies,
                    dont_filter='true', encoding='utf-8', meta={'cookie': cookie, 'proxy': 'http://'+get_proxy()})

    #测试代理ip
    def display_ip(self, response):
        ip = response.xpath('//*[@id="ipd"]/span/text()').extract_first()
        print(ip)

    # 对影院进行爬取，获取所有放映此电影的影院信息
    def parse_cookie(self, response):
        #传入所需要爬取城市的cookie，保证实时性
        cookie = response.meta['cookie']
        #获取城市名
        city = response.css('body > div.header > div > div.city-container > div.city-selected > div::text').extract_first()
        print('正在爬取'+city)

        #判断放映影院是否为空
        if response.css('#app > div.cinemas-list > div.no-cinemas'):
            print('无影院放映此电影')
            pass
        else:
            # 判断是否有两页以上的放映影院，并获取页数
            if response.css('#app > div.cinema-pager > ul > li:nth-last-child(2)'):
                # 总页数
                sum_page = response.css('#app > div.cinema-pager > ul > li:nth-last-child(2) > a::text').extract_first()
                #循环所有影院的页面
                for i in range(0, int(sum_page)):
                    next_page_url = self.start_urls[0] + '&offset=' + str(i * 12)
                    yield Request(url=next_page_url, callback=self.parse_cinema, headers=self.headers,
                                  dont_filter='true', encoding='utf-8', cookies=cookie, meta={'cookie': cookie})
            else:
                #影院的页面只有一页
                yield Request(url=self.start_urls[0], callback=self.parse_cinema, headers=self.headers,
                              dont_filter='true', encoding='utf-8', cookies=cookie, meta={'cookie': cookie})


    #获取电影的影院信息，保存在ying.json
    def parse_cinema(self, response):
        # 传入所需要爬取城市的cookie，保证实时性
        cookie = response.meta['cookie']
        #城市名
        city = response.css('body > div.header > div > div.city-container > div.city-selected > div::text').re('\S+')
        for cinema in response.css('div.cinema-cell'):
            cinema_items = MaoyanItem()
            # 电影的影院链接
            cinema_url = response.urljoin(cinema.css('a::attr(href)').extract_first())

            cinema_items['city'] = city
            cinema_items['href'] = cinema_url
            cinema_items['title'] = cinema.css('a::text').extract_first()
            cinema_items['location'] = cinema.css('p::text').extract_first()


            #对影院链接发送请求，获取影厅信息
            yield scrapy.Request(url=cinema_url, callback=self.parse, headers=self.headers, dont_filter='true',
                                    encoding='utf-8', cookies=cookie)
            #yield ciname_items


    #获取电影“影”的影厅信息，保存在seat.json
    def parse(self, response):
        # 城市名
        city = response.css('body > div.header > div > div.city-container > div.city-selected > div::text').re('\S+')
        #影厅的放映日期
        time1 = response.css('#app > div.show-list.active > div.show-date > span.date-item.active::text').extract_first()[3:] + "号"
        for seat in response.css('#app > div.show-list.active > div.plist-container.active > table > tbody >tr'):
            hall_item = moviehallItem()


            #影厅的放映时间=日期+准确时间
            time2 = seat.css('td:nth-child(1) span.begin-time::text').extract_first()
            hall_url = response.urljoin(seat.css('td:nth-child(5) a::attr(href)').extract_first())

            hall_item['city'] = city
            hall_item['time'] = time1 + time2
            hall_item['language'] = seat.css('td:nth-child(2) span::text').extract_first()
            hall_item['title'] = seat.css('td:nth-child(3) span::text').extract_first()
            hall_item['href'] = hall_url

            #对影厅链接发送请求，获取选座信息
            #yield Request(url=hall_url, callback=self.parse_seat, headers=self.headers, dont_filter='true')
            yield hall_item

    #获取座位选择信息:seat empty代表座位为空，seat selectable代表座位可选择，seat empty代表座位已选择
    def parse_seat(self, response):
        for row in response.css('#app > div.main.clearfix > div.hall > div.seats-block > div.seats-container > div.seats-wrapper > div.row > span.sold'):
            seatnum = seatNumItem()
            #座位售卖
            seatnum['seat'] = row.css('span::attr(class)').extract_first()
            #价格
            price = row.xpath('//*[@id="app"]/div[2]/div[2]/div[2]/div[5]/span[2]/text()').re(r'￥(.*?)/张')[0]
            seatnum['price'] = price
            yield seatnum

