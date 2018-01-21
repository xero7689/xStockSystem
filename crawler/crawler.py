import sys
import pymysql
import requests
import json
import datetime
import time
import logging
from settings import *

def year_generator(start_year=2010, end_year=2017):
    dates = []
    for y in range(start_year, end_year+1):
        year = str(y)
        for m in range(1, 12+1):
            month = str(m)
            if m < 10:
                month = '0{}'.format(month)
            date = '{}{}01'.format(year, month)
            dates.append(date)
    return dates

def crawl_day_avg(stock_no, date):
    if int(date) > 20170923:
        return -1
    request_url = url.format(date, stock_no)
    response = requests.get(request_url)
    if not response.content:
        print("[-] {}".format(date))
        return -1
    data = json.loads(response.content)
    price_data = data.get('data', None)
    if not price_data:
        print('[-] {}'.format(date))
        return -1
    insert_len = len(price_data)
    tmp_sql = []
    for d in price_data:
        # d[0]: date, d[1]: price
        try:
            price_date = d[0]
            price = d[1]
            price_date = price_date.split('/')
            price_year = price_date[0].strip()
            price_year = str(int(price_year) + 1911)
            price_month = price_date[1]
            price_day = price_date[2]
            sql_date = "{}-{}-{}".format(price_year, price_month, price_day)
            tmp_sql.append("('{}', '{}')".format(sql_date, d[1]))
        except:
            print('[-] {}'.format(date))
            continue
        print("[+] {}".format(date))

    value_sql = ",".join(tmp_sql)
    sql = batch_insert_sql.format(stock_no, value_sql)
    response = cursor.execute(sql)
    db.commit()

if __name__ == '__main__':
    db = pymysql.connect(HOST, USER, PASSWORD, 'taiwan_stock')
    cursor = db.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS `{}_day_avg` (
      `date` date DEFAULT NULL UNIQUE,
      `price` double DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    batch_insert_sql = """
    INSERT IGNORE INTO {}_day_avg
    (date, price)
    VALUES {}
    """

    #stock_no = sys.argv[1]
    stock_no = [1101, 1102, 1103, 1104, 1108, 1109, 1110]
    url = 'http://www.tse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date={}&stockNo={}'

    dates = year_generator()

    db.commit()
    for sno in stock_no:
        cursor.execute(create_table_sql.format(sno))
        for date in dates:
            crawl_day_avg(sno, date)
            time.sleep(5)
        
        
