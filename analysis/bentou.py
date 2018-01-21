import os, sys
import pandas as pd
import datetime
from analyze_stock import *
from lib.mysql import get_stock_info

def count_bentou(stock_id, start_date, end_date, delta=7, pr=0.02):
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
        return 0

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    mean_price = pd.DataFrame.mean(df['price'][mask])
    #print('{}-{}\tmean: {}'.format(start_date, end_date, mean_price))

    tmp_start = start_date
    count = 0
    while True:
        tmp_fin = tmp_start + datetime.timedelta(days=delta)
        if tmp_fin > end_date:
            break
        else:
            tmp_mask = (df['date'] >= tmp_start) & (df['date'] <= tmp_fin)
            tmp_mask_price = df['price'][tmp_mask]
            if len(tmp_mask_price) == 0:
                #print('Empty sequence')
                return 0

            # Find Max and Min Price
            tmp_max_p = max(tmp_mask_price)
            tmp_min_p = min(tmp_mask_price)
            if (tmp_max_p / mean_price)-1 > pr:
                count += 1
            if 1-(tmp_min_p / mean_price) > pr:
                count += 1
            tmp_start = tmp_fin
    return count


