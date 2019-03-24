import sys, os
from pprint import pprint
import pymysql
import random

from utils import year_generator
from daily import *
from proxy_pool import ProxyPool
from settings import *

pp = ProxyPool()

if __name__ == '__main__':
    sid = int(sys.argv[1])
    use_proxy = int(sys.argv[2])
    start = int(sys.argv[3])
    for date in year_generator(start_year=start):
        print(date)
        dd = crawl_daily_data(sid, date, use_proxy)
        if dd:
            insert_daily_data(sid, dd)
        bd = crawl_daily_bwibbw(sid, date, use_proxy)
        if bd:
            insert_bwibbw_data(sid, bd)
        time.sleep(random.randint(5, 15))
