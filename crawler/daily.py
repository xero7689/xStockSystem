# -*- coding: utf-8 -*-
"""
TWSEC Daily Information Crawler

Todo:
    - http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}

Done:
    - http://www.tse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date={}&stockNo={}
    - http://www.tse.com.tw/exchangeReport/BWIBBU?response=json&date={}&stockNo={}

Issue:
    - Daily date larger than 2018
"""

import sys, os
import re
import ipdb
import json
import pymysql
import requests
import datetime
import time

from proxyq import ProxyQueue
from utils import year_generator
from color_print import color_print
from settings import USER, PASSWORD
db = pymysql.connect('127.0.0.1', USER, PASSWORD, 'taiwan_stock',
                     charset='utf8')
cursor = db.cursor()

insert_daily_sql = """
INSERT IGNORE INTO daily
(date, stock_id, price, yield, pe, pbr)
VALUES
(%s, %s, %s, %s, %s, %s)
"""

price_url = 'http://www.tse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date={}&stockNo={}'

bwibbw_url = 'http://www.tse.com.tw/exchangeReport/BWIBBU?response=json&date={}&stockNo={}'

headers = { 'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/61.0.3163.100 Chrome/61.0.3163.100 Safari/537.36',
        'Referer': 'http://www.tse.com.tw/zh/page/trading/exchange/BWIBBU.html'
        }

# Get Stock_id
_get_sid = """
SELECT stock_id FROM stock_list
"""

# Global proxy queue
proxy_queue = ProxyQueue()

def crawl_daily(date, sid):
    global proxy_queue
    delay, (pid, ip, port) = proxy_queue.get()
    proxy = {'http': 'http://{}:{}'.format(ip, port)}
    print('Use proxy {}'.format(proxy))

    color_print('[*] Stock_id {} on {}'.format(sid, date), 'blue')
    daily_data = {}
    if int(date) >= int(datetime.datetime.now().strftime('%Y%m%d')):
        return -1

    cursor = db.cursor()
    color_print('  --> Fetch Bwibbu data', 'yellow')
    bwibbw_response = requests.get(bwibbw_url.format(date, sid), headers=headers)
    try:
        bwibbw_data = json.loads(bwibbw_response.content)['data']
    except Exception as e:
        stat = json.loads(bwibbw_response.content)['stat']
        print(stat)
        return -1

    color_print('  --> Fetch Price data', 'yellow')
    max_retry = 5
    while True:
        try:
            price_response = requests.get(price_url.format(date, sid), headers=headers)
            price_data = json.loads(price_response.content)['data']
            break
        except KeyError as ke:
            if max_retry > 0:
                color_print('[!] Key Error, max retry {}.'.format(max_retry),
                            'red')
                time.sleep(10)
                continue
            else:
                raise ke


    for data in bwibbw_data:
        _date = data[0]
        year, month, day = re.findall('\d+[\u0000-\u007F]', _date)
        year = 1911 + int(year)
        _date = "{}-{}-{}".format(year, month, day)
        if int(date) < 20170401:
            try:
                pe = float(data[1])
            except ValueError:
                pe = None
            try:
                y = float(data[2])
            except ValueError:
                y = None
            try:
                pbr = float(data[3])
            except ValueError:
                pbr = None
            daily_data[(sid, _date)] = {'price': 0, 'yield': y, 'pe': pe, 'pbr': pbr}
        else:
            try:
                y = float(data[1])
            except ValueError:
                y = None

            try:
                pe = float(data[3])
            except ValueError:
                pe = None
            
            try:
                pbr = float(data[4])
            except ValueError:
                pbr = None
            daily_data[(sid, _date)] = {'price': 0, 'yield': y, 'pe': pe, 'pbr': pbr}


    for data in price_data[:-1]:
        year, month, day = data[0].split('/')
        year = 1911 + int(year)
        _date = "{}-{}-{}".format(year, month, day)
        try:
            price = float(data[1])
        except ValueError as ve:
            """
            If data in twse has no price after 2017/04/01
            it may contains '--' in field
            """
            print('No price data founded!')
            price = None
        try:
            daily_data[(sid, _date)]['price'] = price
        except KeyError as ke:
            """
            Sometimes TWSEC may have price data but BWIBBU data
            """
            daily_data[(sid, _date)] = {'price': price, 'yield': None, 'pe':
                                        None, 'pbr': None}
            

    try:
        daily_iter = daily_data.iteritems()
    except AttributeError:
        daily_iter = daily_data.items()
    for k, v in daily_iter:
        sid, date = k
        args = (date, sid, v['price'], v['yield'], v['pe'], v['pbr'])
        color_print('    --> ${} | {} | {} | {}'.format(v['price'],
                                                       v['pe'],
                                                       v['yield'],
                                                       v['pbr']),
                   'green')
        cursor.execute(insert_daily_sql, args=args)

    db.commit()
    print('[+] {} - {}'.format(date, sid))
    cursor.close()

if __name__ == '__main__':
    # Sid List
    cursor = db.cursor()
    _get_by_cate = """
    select stock_id from stock_list where stock_cate = %s
    """

    # 化學-1747
    cate_list = ['電子零組件']

    for cate in cate_list:
        cursor.execute(_get_by_cate, (cate,))
        sid_lists = cursor.fetchall()
        db.commit()
        # Full Update
        for sid in sid_lists:
            sid = sid[0]
            #if sid == '2002A':
            #    continue
            #if int(sid) < 1590:
            #    print(sid)
            #    continue
            for date in year_generator(start_year=2012):
                crawl_daily(date, sid)
                time.sleep(1)

    """
    #crawl_daily(20130430, 2597)
    for date in year_generator(start_year=2011):
        crawl_daily(date, 1307)
        time.sleep(5)
    """
