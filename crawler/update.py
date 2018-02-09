import sys, os
import datetime
import time
import random
from daily import *
from lib.mysqlqueue import StockMySQL
from settings import USER, PASSWORD
from utils import until_today_generator

def find_update_date(sid):
    date_list = []
    db = StockMySQL('127.0.0.1', USER, PASSWORD, 'taiwan_stock')
    latest_date = db.select_latest_date_by_sid(sid)[0][0]
    today = datetime.datetime.today().date()
    delta_days = (today - latest_date).days
    for x in range(0, delta_days):
        date_list.append(today - datetime.timedelta(days=x))
    return date_list

if __name__ == '__main__':
    sid = int(sys.argv[1])
    date_list = find_update_date(sid)
    cur_month = None
    for date in until_today_generator(2017):
        """
        # Parse date
        year = date.year
        month = date.month
        if month == cur_month:
            continue
        else:
            cur_month = month
        day = date.day
        if month < 10:
            month = "0{}".format(month)
        if day < 10:
            day = "0{}".format(day)
        _date = "{}{}{}".format(year, month, day)
        """

        # Crawl
        #crawl_daily(_date, sid)
        dd = crawl_daily_data(sid, date, False)
        bd = crawl_daily_bwibbw(sid, date, False)
        insert_daily_data(sid, dd)
        insert_bwibbw_data(sid, bd)
        time.sleep(random.randint(5, 15))
