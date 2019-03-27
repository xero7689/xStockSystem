# -*- coding: utf-8 -*-
import sys, os
import pymysql
import csv
from conf.settings import *

OUTPUT_DIR = './report'

date = sys.argv[1]
cate = sys.argv[2]

con = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, 'taiwan_stock',
                      charset='utf8')
cursor = con.cursor()

_select_yield = """
select d.stock_id, sl.zh_name, truncate(avg(d.price), 2), truncate(avg(d.pe),
2) as ape, truncate(avg(yield), 2),
truncate(avg(pbr), 2), max(d.date) as '最新資料日期'
from daily as d inner join stock_list as sl on d.stock_id =
sl.stock_id where d.date >= %s and d.pe is not NULL and
sl.stock_cate = %s group by
d.stock_id order by avg(yield) desc limit 50;
"""

_select_pbr = """
select sl.zh_name, sl.stock_id, mpbr, dd, sl.stock_cate from stock_list as sl inner join (select d.stock_id,truncate(avg(d.pbr), 2) as mpbr, d.date as dd from daily as d where date > '2017-01-01' group by d.stock_id) as d on d.stock_id = sl.stock_id order by mpbr desc;
"""

cursor.execute(_select, (date, cate))
data = cursor.fetchall()

fn = date + '_' + cate + '_rank.csv'
with open(os.path.join(OUTPUT_DIR, fn), 'w+') as f:
    for row in data:
        row = [str(r) for r in row]
        f.write(', '.join(row) + '\n')
