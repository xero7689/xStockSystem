# -*- coding: utf-8 -*-

import requests
from lxml import etree
import re
import time

from date_handler import year_generator
from bwibbu_crawler import BWIBBU_Crawler

dates = year_generator()
bwibbu_crawler = BWIBBU_Crawler()

list_url = 'https://tw.stock.yahoo.com/h/kimosel.php?tse=1&cat=%E9%87%91%E8%9E%8D&form=menu&form_id=stock_id&form_name=stock_name&domain=0'

response = requests.get(list_url)
print response.content

tree = etree.HTML(response.content)

elements = tree.xpath('.//a[@class="none"]/text()')
for e in elements:
    stock_no, stock_name = e.split(' ')
    stock_no = stock_no.strip()
    stock_name = stock_name.strip()
    print("{} - {}".format(stock_no, stock_name.encode('utf8')))
    if int(stock_no[:4]) <= 2892:
        continue
    for date in dates:
        bwibbu_crawler.crawl(stock_no, date)
        time.sleep(5)

