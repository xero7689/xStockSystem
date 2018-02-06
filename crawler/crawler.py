import sys, os
from pprint import pprint
import pymysql
import random

from utils import year_generator
from daily import *
from proxy_pool import ProxyPool
from settings import *

pp = ProxyPool()

def get_cate_stock(cate_name):
    sql = """
        SELECT stock_id from stock_list
        WHERE stock_cate = %s
    """
    sidlist = []
    con = pymysql.connect(HOST, USER, PASSWORD, 'taiwan_stock', charset='utf8')
    cursor = con.cursor()
    cursor.execute(sql, (cate_name,))
    response = cursor.fetchall()
    cursor.close()
    con.close()
    for sid in response:
        sidlist.append(sid[0])
    return sidlist

if __name__ == '__main__':
    sid = int(sys.argv[1])
    use_proxy = int(sys.argv[2])
    for date in year_generator(start_year=2012):
        print(date)
        dd = crawl_daily_data(sid, date, use_proxy)
        if dd:
            insert_daily_data(sid, dd)
        bd = crawl_daily_bwibbw(sid, date, use_proxy)
        if bd:
            insert_bwibbw_data(sid, bd)
        time.sleep(random.randint(5, 15))
