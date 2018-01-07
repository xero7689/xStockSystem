# -*- coding: utf-8 -*-

import sys, os
import pymysql
import requests
from lxml import etree
import re
import time

try:
    import urlparse  # For python2
except ImportError:
    import urllib.parse as urlparse  # For python3

from date_handler import year_generator
from settings import USER, PASSWORD

# Yahoo Settings
YAHOO_URL = 'https://tw.stock.yahoo.com'

# Fake Headers
fake_header = {}
fake_header['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0"
fake_header['Accept-Language'] = 'en-US,en;q=0.5'
fake_header['Accept-Encoding'] = 'gzip, deflate, br'
fake_header['Referer'] = 'https://www.google.com.tw/'

# Mysql Settings
db = pymysql.connect('localhost', USER, PASSWORD, 'taiwan_stock', charset='utf8')
db.commit()
cursor = db.cursor()

_create = """
CREATE TABLE IF NOT EXISTS stock_list
(
    id mediumint NOT NULL AUTO_INCREMENT,
    stock_id varchar(255) NOT NULL,
    zh_name varchar(255) DEFAULT NULL,
    eng_name varchar(255) DEFAULT NULL,
    stock_cate varchar(255) DEFAULT NULL,
    PRIMARY KEY (id)
);
"""

_insert = """
INSERT IGNORE INTO stock_list
(stock_id, zh_name)
VALUES (%s, %s)
"""

_insert = """
INSERT IGNORE INTO stock_list
(stock_id, zh_name)
VALUES (%s, %s)
"""

_insert_with_cate = """
INSERT IGNORE INTO stock_list
(stock_id, zh_name, stock_cate)
VALUES (%s, %s, %s)
"""


cursor.execute(_create)
db.commit()

# Get Stock No
def crawl_yahoo_stock_id(cate_href, cate_name=None):
    cursor = db.cursor()
    response = requests.get(cate_href)
    tree = etree.HTML(response.content)

    elements = tree.xpath('.//a[@class="none"]/text()')
    for e in elements:
        stock_no, stock_name = e.split(' ')
        stock_no = stock_no.strip()
        stock_name = stock_name.strip()
        stock_name = stock_name.encode('utf8')
        #import ipdb
        #ipdb.set_trace()
        #cursor.execute(sql, (stock_no, stock_name))
        if not cate_name:
            cursor.execute(_insert, (stock_no, stock_name))
        else:
            cursor.execute(_insert_with_cate, (stock_no, stock_name, cate_name))
        print(str(stock_name))
        #print("{} - {}".format(stock_no, stock_name))
    db.commit()


# Get Category List
CATEGORY_BASE_URL = 'https://tw.stock.yahoo.com/h/kimosel.php'
cat_response = requests.get(CATEGORY_BASE_URL, headers=fake_header)
cat_tree = etree.HTML(cat_response.content)
stock_categories = cat_tree.xpath('.//td[@class="c3"]/a')

for category_a in stock_categories:
    cate = category_a.text
    href = category_a.attrib['href']
    category_url = urlparse.urljoin(YAHOO_URL, href)
    print('[*] {}'.format(category_url.encode('utf8')))
    crawl_yahoo_stock_id(category_url, cate)
    time.sleep(1)

