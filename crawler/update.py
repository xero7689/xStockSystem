import sys, os
import datetime
import time
import random

from lib.daily import *
from lib.mysqlqueue import StockMySQL
from lib.utils import until_today_generator
from conf.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD

def find_update_date(sid):
    date_list = []
    db = StockMySQL(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, 'taiwan_stock')
    latest_date = db.select_latest_date_by_sid(sid)[0][0]
    today = datetime.datetime.today().date()
    delta_days = (today - latest_date).days
    for x in range(0, delta_days):
        date_list.append(today - datetime.timedelta(days=x))
    return date_list

if __name__ == '__main__':
    db = StockMySQL(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, 'taiwan_stock')
    sid = int(sys.argv[1])
    use_proxy = int(sys.argv[2])
    date_list = find_update_date(sid)
    for date in until_today_generator(2018):
        dd = crawl_daily_data(sid, date, use_proxy)
        bd = crawl_daily_bwibbw(sid, date, use_proxy)
        insert_daily_data(sid, dd)
        insert_bwibbw_data(sid, bd)
        time.sleep(random.randint(5, 15))
