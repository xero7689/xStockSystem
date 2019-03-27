# -*- coding: utf-8 -*-
""" Stock ID Crawler from tw.stock.yahoo.com
"""

import sys, os
import re
import requests
import pymysql

from bs4 import BeautifulSoup
from lxml import etree

from conf.settings import *

url = 'https://tw.stock.yahoo.com/h/kimosel.php?tse=1&cat=%E5%8D%8A%E5%B0%8E%E9%AB%94&form=menu&form_id=stock_id&form_name=stock_name&domain=0'

sql = """
INSERT INTO stock_info 
(sid, zh_name) 
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE
sid = %s,
zh_name = %s
"""

DB_NAME = 'twse'

db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, DB_NAME)
cursor = db.cursor()

response = requests.get(url)
content = response.content
tree = etree.HTML(content)
for element in tree.xpath('.//a[@class="none"]/text()'):
    sid, s_name = element.split(' ')
    sid = sid.strip()
    s_name = s_name.encode('utf8')
    print(sid, s_name)
    cursor.execute(sql, (sid, s_name, sid, s_name))
db.commit()
cursor.close()
