import datetime
import time
from daily import crawl_daily
from lib.mysqlqueue import StockMySQL

def find_update_date(sid):
    date_list = []
    db = StockMySQL('127.0.0.1', 'xero', 'uscrfycn', 'taiwan_stock')
    latest_date = db.select_latest_date_by_sid(sid)[0][0]
    today = datetime.datetime.today().date()
    delta_days = (today - latest_date).days
    for x in range(0, delta_days):
        date_list.append(today - datetime.timedelta(days=x))
    return date_list

if __name__ == '__main__':
    sid = 1101
    date_list = find_update_date(sid)
    for date in date_list:
        # Parse date
        year = date.year
        month = date.month
        day = date.day
        if month < 10:
            month = "0{}".format(month)
        if day < 10:
            day = "0{}".format(day)
        _date = "{}{}{}".format(year, month, day)

        # Crawl
        crawl_daily(_date, sid)
        time.sleep(10) 
