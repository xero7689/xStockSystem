# -*- coding: utf-8 -*-
"""
TWSEC Daily Information Crawler

Done:
    - http://www.tse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}

    - http://www.tse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date={}&stockNo={}
    - http://www.tse.com.tw/exchangeReport/BWIBBU?response=json&date={}&stockNo={}

Issue:
    - Daily date larger than 2018
"""

import sys, os
import re
import json
import pymysql
import requests
import datetime
import time
import collections

from proxyq import ProxyQueue
from utils import year_generator
from color_print import color_print
from settings import USER, PASSWORD

from lib.mylogger import MyLogger
from proxy_pool import ProxyPool


# Logger
logger = MyLogger(name='daily_crawler')

db = pymysql.connect('127.0.0.1', USER, PASSWORD, 'taiwan_stock',
                     charset='utf8')
cursor = db.cursor()

insert_bwibbw_sql = """
INSERT IGNORE INTO daily
(date, stock_id, yield, pe, pbr)
VALUES
(%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
yield=%s, pe=%s, pbr=%s
"""

insert_daily_sql = """
INSERT IGNORE INTO daily
(date, stock_id, price, op, max, min, pd, lot, vol)
VALUES
(%s, %s, %s, %s, %s, %s, %s, %s, %s)
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

no_match_data_byte_string = b'\xe5\xbe\x88\xe6\x8a\xb1\xe6\xad\x89\xef\xbc\x8c\xe6\xb2\x92\xe6\x9c\x89\xe7\xac\xa6\xe5\x90\x88\xe6\xa2\x9d\xe4\xbb\xb6\xe7\x9a\x84\xe8\xb3\x87\xe6\x96\x99!'.decode('utf8')
# Get Stock_id
_get_sid = """
SELECT stock_id FROM stock_list
"""

# Global proxy queue
proxy_pool = ProxyPool()

def _get_twsec_data(twsec_url, headers=None, use_proxy=False):
    max_retry = 5
    data = None
    while True:
        try:
            if use_proxy:
                ip, port, delay, count = proxy_pool.get()
                if not ip:
                    print('no proxy can use')
                    use_proxy = None
                    continue
                proxies = {
                    'http': 'http://{}:{}'.format(ip, port),
                    'https': 'http://{}:{}'.format(ip, port)
                }
                start = time.time()
                response = requests.get(twsec_url, headers=headers, proxies=proxies, timeout=5)
                color_print(response.status_code, 'red')
                delay = time.time() - start
                proxy_pool.release(ip, port, count, delay)
            else:
                response = requests.get(twsec_url, headers=headers)

            if type(response.content) is bytes:
                content = response.content.decode('utf8')
            else:
                content = response.content
            
            json_obj = json.loads(content)
            # No condition match data, directly jump out!
            if json_obj['stat'] == no_match_data_byte_string:
                color_print(json_obj['stat'], 'red')
                data = None
                break
            else:
                data = json_obj['data']
                break
        except KeyError as ke:
            if max_retry > 0:
                color_print('[!] Key Error, max retry {}.'.format(max_retry),
                            'red')
                color_print(response.content, 'yellow')
                time.sleep(10)
                max_retry -= 1
                continue
            else:
                logger.DEBUG(ke)
                return None
        except json.decoder.JSONDecodeError as jde:
            print (response.content)
            print (jde)
            return data
        except requests.exceptions.Timeout:
            delay = time.time() - start
            proxy_pool.release(ip, port, count, delay)
            continue
        except Exception as e:
            try:
                if e.args[0].args[1].args[0] == 104:
                    print(e.args[0].args[1].args[1])
                    continue
            except IndexError:
                logger.error(e)
                continue
    return data

def _parse_daily_data(daily_data):
    data = {}
    for d in daily_data:
        year, month, day = d[0].split('/')
        year = 1911 + int(year)
        _date = "{}-{}-{}".format(year, month, day)
        if year > 2020:
            import ipdb
            ipdb.set_trace()
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

def consist_bwibbw_date(bwibbw_data):
    year_list = []
    month_list = []
    for d in bwibbw_data:
        date = d[0]
        year, month, day = re.findall('\d+[\u0000-\u007F]', date)
        year_list.append(year)
        month_list.append(month)
    yc = collections.Counter(year_list)
    mc = collections.Counter(month_list)
    real_year = max(collections.Counter(yc).items(), key=lambda x:x[1])[0]
    real_month = max(collections.Counter(mc).items(), key=lambda x:x[1])[0]
    return (real_year, real_month)

def _parse_daily_bwibbw(bwibbw_data):
    data = {}
    ry, rm = consist_bwibbw_date(bwibbw_data)
    for d in bwibbw_data:
        date = d[0]
        year, month, day = re.findall('\d+[\u0000-\u007F]', date)
        if year != ry:
            year = ry
        if month != rm:
            month = rm
        year = 1911 + int(year)
        int_date = int(str(year)+month+day)
        _date = "{}-{}-{}".format(year, month, day)
        if year > 2020:
            import ipdb
            ipdb.set_trace()

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
            except IndexError:
                import ipdb
                ipdb.set_trace()
            data[_date] = {'price': 0, 'yield': y, 'pe': pe, 'pbr': pbr}
    return data

def crawl_daily_bwibbw(sid, date, use_proxy=False):
    """
        Crawl BWIBBW Data 
    """
    color_print('  --> Fetch Bwibbu data', 'yellow')
    data = _get_twsec_data(bwibbw_url.format(date, sid), headers=headers, use_proxy=use_proxy)
    if not data:
        data = None
    else:
        data = _parse_daily_bwibbw(data)
    return data

def crawl_daily_data(sid, date, use_proxy=False):
    # Fetch Data
    color_print('  --> Fetch daily data', 'yellow')
    data = _get_twsec_data(max_min_url.format(date, sid), headers=headers, use_proxy=use_proxy)
    if not data:
        data = None
    else:
        data = _parse_daily_data(data)
    return data

def insert_daily_data(sid, data):
    try:
        daily_iter = data.iteritems()
    except AttributeError:
        daily_iter = data.items()
    cursor = db.cursor()
    for date, info in daily_iter:
        _price = info['cp']
        _op = info['op']
        _max = info['max']
        _min = info['min']
        _d = info['delta']
        _lot = info['lot']
        _vol = info['vol']
        args = (date, sid, _price, _op, _max, _min, _d, _lot, _vol, 
                            _price, _op, _max, _min, _d, _lot, _vol)
        #color_print('    --> ${} | {} | {} | {}'.format(
        #                    info['cp'], info['op'], info['max'], info['min']) ,'green')
        cursor.execute(insert_daily_sql, args=args)
    db.commit()

def insert_bwibbw_data(sid, data):
    try:
        _iter = data.iteritems()
    except AttributeError:
        _iter = data.items()
    cursor = db.cursor()
    for date, info in _iter:
        _yield = info['yield']
        _pe = info['pe']
        _pbr = info['pbr']
        args = (date, sid, _yield, _pe, _pbr, _yield, _pe, _pbr)
        #color_print('    --> {} | {} | {}'.format(_yield, _pe, _pbr), 'green')
        cursor.execute(insert_bwibbw_sql, args=args)
    db.commit()

