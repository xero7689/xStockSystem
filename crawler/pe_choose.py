import sys
import pymysql
import datetime
from conf.settings import *

class pe_obj(object):
    def __init__(self, year):
        pass

if __name__ == '__main__':
    stock_no = sys.argv[1]
    db = pymysql.connect(HOST, USER, PASSWORD, 'taiwan_stock')
    cursor = db.cursor()
    sql = 'select * from {}_bwibbu'.format(stock_no)
    cursor.execute(sql)
    datas = cursor.fetchall()
    db.commit()
    cursor.close()

    pe_dict = {}
    eps_dict = {'2014': 1.13, '2015': 1.22, '2016': 1.16, '2017': 0.59*3}
    eps_2317 = {'2014': 8.85, '2015': 9.42, '2016': 8.6, '2017': 2.66*3}


    for data in datas:
        try:
            pe = data[1]
        except:
            continue
        if pe == 0.0:
            continue
        key = data[0].year
        if key not in pe_dict:
            pe_dict[key] = [pe]
        else:
            pe_dict[key].append(pe)

    for year, pe_list in pe_dict.iteritems():
        if year < 2014:
            continue
        try:
            eps = eps_2317[str(year)]
        except KeyError as ke:
            print(year)
            continue
        _min = min(pe_list)*eps
        _avg = (sum(pe_list)/len(pe_list))*eps
        _max = max(pe_list)*eps
        print("{}: {}\t{:.2f}\t{}".format(year, _min, _avg, _max))


 
