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

from lib.mylogger import MyLogger


# Logger
logger = MyLogger(name='daily_crawler')

db = pymysql.connect('127.0.0.1', USER, PASSWORD, 'taiwan_stock',
                     charset='utf8')
cursor = db.cursor()

insert_bwibbw_sql = """
INSERT IGNORE INTO daily
(date, stock_id, price, yield, pe, pbr)
VALUES
(%s, %s, %s, %s, %s, %s)
"""

insert_daily_sql = """
INSERT INTO daily
(date, stock_id, price, op, max, min, pd, lot, vol)
VALUES
(%s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
price=%s, op=%s, max=%s, min=%s, pd=%s, lot=%s, vol=%s
"""

update_max_min = """
UPDATE daily
SET op=%s, max=%s, min=%s, pd=%s, lot=%s, vol=%s
WHERE stock_id = %s
AND date = %s
"""

price_url = 'http://www.tse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date={}&stockNo={}'

bwibbw_url = 'http://www.tse.com.tw/exchangeReport/BWIBBU?response=json&date={}&stockNo={}'

max_min_url = 'http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}'

headers = { 'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/61.0.3163.100 Chrome/61.0.3163.100 Safari/537.36',
        'Referer': 'http://www.tse.com.tw/zh/page/trading/exchange/BWIBBU.html'
        }

# Get Stock_id
_get_sid = """
SELECT stock_id FROM stock_list
"""

# Global proxy queue
proxy_queue = ProxyQueue()

def _get_twsec_data(twsec_url, headers=None, proxies=None):
    max_retry = 5
    while True:
        try:
            response = requests.get(twsec_url, headers=headers)
            data = json.loads(response.content)['data']
            break
        except KeyError as ke:
            if max_retry > 0:
                color_print('[!] Key Error, max retry {}.'.format(max_retry),
                            'red')
                time.sleep(10)
                continue
            else:
                logger.DEBUG(ke)
                return None
        except Exception as e:
            print(response.content)
            raise e
    return data

def _parse_daily_data(daily_data):
    data = {}
    for d in daily_data:
        year, month, day = d[0].split('/')
        year = 1911 + int(year)
        _date = "{}-{}-{}".format(year, month, day)
        data[_date] = {
            'lot'    : d[1],
            'total'  : d[2],
            'op'     : d[3],
            'max'    : d[4],
            'min'    : d[5],
            'cp'     : d[6],
            'delta'  : d[7],
            'vol'    : d[8]
        }
    return data

def _parse_daily_bwibbw(bwibbw_data):
    data = {}
    for d in bwibbw_data:
        date = d[0]
        year, month, day = re.findall('\d+[\u0000-\u007F]', date)
        int_date = int(year+month+day)
        year = 1911 + int(year)
        _date = "{}-{}-{}".format(year, month, day)
        if int_date < 20170401:
            try:
                pe = float(d[1])
            except ValueError:
                pe = None
            try:
                y = float(d[2])
            except ValueError:
                y = None
            try:
                pbr = float(d[3])
            except ValueError:
                pbr = None
            data[_date] = {'price': 0, 'yield': y, 'pe': pe, 'pbr': pbr}
        else:
            try:
                y = float(d[1])
            except ValueError:
                y = None

            try:
                pe = float(d[3])
            except ValueError:
                pe = None
            
            try:
                pbr = float(d[4])
            except ValueError:
                pbr = None
            data[_date] = {'price': 0, 'yield': y, 'pe': pe, 'pbr': pbr}
    return data

def crawl_daily_bwibbw(sid, date):
    """
        Crawl BWIBBW Data 
    """
    color_print('  --> Fetch Bwibbu data', 'yellow')
    data = _get_twsec_data(bwibbw_url.format(date, sid), headers=headers)
    data = _parse_daily_bwibbw(data)
    return data

def crawl_daily_data(sid, date):
    # Fetch Data
    color_print('  --> Fetch daily data', 'yellow')
    data = _get_twsec_data(max_min_url.format(date, sid), headers=headers)
    data = _parse_daily_data(data)
    return data

def insert_daily_data(sid, data):
    try:
        daily_iter = data.iteritems()
    except AttributeError:
        daily_iter = data.items()
    cursor = db.cursor()
    for date, info in daily_iter:
        args = (date, sid, info['cp'], info['op'], 
                           info['max'], info['min'],
                           info['pd'], info['lot'], info['vol'])
        color_print('    --> ${} | {} | {} | {}'.format(
                            info['cp'], info['op'], info['max'], info['min']) ,'green')
        cursor.execute(insert_daily_sql, args=args)

def crawl_daily_found(date, sid):
    """
    global proxy_queue
    delay, (pid, ip, port) = proxy_queue.get()
    proxy = {'http': 'http://{}:{}'.format(ip, port)}
    print('Use proxy {}'.format(proxy))
    """

    color_print('[*] Stock_id {} on {}'.format(sid, date), 'blue')
    daily_data = {}
    if int(date) >= int(datetime.datetime.now().strftime('%Y%m%d')):
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

    
            

    try:
        daily_iter = daily_data.iteritems()
    except AttributeError:
        daily_iter = daily_data.items()
    

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
    """
    for cate in cate_list:
        cursor.execute(_get_by_cate, (cate,))
        sid_lists = cursor.fetchall()
        db.commit()
        # Full Update
        for sid in sid_lists:
            sid = sid[0]
            #if sid == '2002A':
            #    continue
            try:
                sid = int(sid)
            except:
                continue
            if sid <= 2838:
                continue
            for date in year_generator(start_year=2012):
                crawl_daily(date, sid)
                time.sleep(1)
    """
    """
    #crawl_daily(20130430, 2597)
    for date in year_generator(start_year=2011):
        crawl_daily(date, 1307)
        time.sleep(5)
    """
    data = crawl_daily_data(2597, 20130430)
    #print(crawl_daily_bwibbw(2597, 20130430))
    insert_daily_data(2597, data)
