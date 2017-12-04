# -*- coding: utf-8 -*-

import pymysql
import requests
import json
import datetime
import time
import re

class BWIBBU_Crawler(object):
    bwibbu_url = 'http://www.tse.com.tw/exchangeReport/BWIBBU?response=json&date={}&stockNo={}'
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS `{}_bwibbu` (
      `date` date DEFAULT NULL UNIQUE,
      `pe_rate` double DEFAULT NULL,
      `yield_rate` double DEFAULT NULL,
      `pbr` double DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    batch_insert_sql = """
    INSERT IGNORE INTO {}_bwibbu
    (date, pe_rate, yield_rate, pbr)
    VALUES {}
    """
    def __init__(self):
        self.db_con = pymysql.connect('localhost', 'xero', 'uscrfycn', 'taiwan_stock')

    def date_is_out_of_range(self, date):
        current_date = int(datetime.datetime.now().strftime('%Y%m01'))
        return int(date) > current_date

    def crawl(self, stock_no, date, dates=None):
        # Bound Check
        if self.date_is_out_of_range(date):
            print('[Warning] Date is out of range!')
            return -1

        # Init Curor
        cursor = self.db_con.cursor()

        # Init Table
        cursor.execute(self.create_table_sql.format(stock_no))
        self.db_con.commit()
        
        # Request
        request_url = self.bwibbu_url.format(date, stock_no)
        response = requests.get(request_url)
        if not response.content:
            print("[Warning] No content founded!")
            return -1
        
        # Preprocess
        data = json.loads(response.content)
        bwibbu_data = data.get('data', None)
        if not bwibbu_data:
            print('[Warning] {}'.format(data.get('state')))
            return -1
        
        insert_len = len(bwibbu_data)
        tmp_sql = []
        for d in bwibbu_data:
            # d[0]: date, d[1]: price
            price_date = d[0]
            price_date = re.findall(u'(.*?)年(.*?)月(.*?)日', price_date) 
            price_year = price_date[0][0].strip()
            price_year = str(int(price_year) + 1911)
            price_month = price_date[0][1]
            price_day = price_date[0][2]
            sql_date = "{}-{}-{}".format(price_year, price_month, price_day)
            if date < '20170401':
                per = d[1]
                dy = d[2]
                pbr = d[3]
            else:
                per = d[3]
                dy = d[1]
                pbr = d[4]
            format_template = "('{}', '{}', '{}', '{}')" 
            tmp_sql.append(format_template.format(sql_date, per, dy, pbr))

        value_sql = ",".join(tmp_sql)
        sql = self.batch_insert_sql.format(stock_no, value_sql)
        response = cursor.execute(sql)
        print("[+] {}".format(date))
        self.db_con.commit()
        cursor.close()

if __name__ == '__main__':
    crawler = BWIBBU_Crawler()
    crawler.crawl(2330, '20170401')
