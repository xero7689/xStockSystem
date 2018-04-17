# -*- coding: utf-8 -*-
""" Back test prototype program
"""
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from analyze_stock import align_price_by_date
from lib.mysql import get_stock_info

if __name__ == '__main__':
    stock_id = 2353
    start_date = '2014-01-01'
    end_date = '2018-03-31'

    vol = 1000
    fees_rate = 0.001425
    tax_rate = 0.003

    df = get_stock_info(stock_id)
    try:
        df['date'] = pd.to_datetime(df['date'])
        #df = df.sort('date')
    except Exception as e:
        #print(e)
        for row in df['date'].iteritems():
            try: 
                pd.to_datetime(row[1]) 
            except: 
                print(row[1])
        raise e

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)

    
    end_price = df['price'][mask][-1:].values[0]
    #print(end_price)
    #print(pd.Series(df['price'].values, index=df['date']))

    income = []
    sell = end_price * vol * (1 + tax_rate + fees_rate)
    for price in df['price'][mask]:
        buy = price * vol * (1 + fees_rate)
        print(sell-buy)
        income.append((sell-buy)/buy)
    print(type(sell))
    print(type(buy))
    plt.plot(income)
    plt.show()
    

