import os, sys
import pandas as pd
import datetime
from lib.mysql import *
from analyze_stock import *

def count_bentou(stock_id):
    df = get_stock_info(stock_id)
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        #print(e)
        for row in df['date'].iteritems():
            try: 
                pd.to_datetime(row[1]) 
            except: 
                print(row[1])
        raise e
        return 0

    start_date = datetime.datetime(2017, 10, 1)
    end_date = datetime.datetime(2017, 12, 31)
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    mean_price = pd.DataFrame.mean(df['price'][mask])
    #print('{}-{}\tmean: {}'.format(start_date, end_date, mean_price))

    tmp_start = start_date
    count = 0
    while True:
        tmp_fin = tmp_start + datetime.timedelta(days=7)
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
            if (tmp_max_p / mean_price)-1 > 0.02:
                count += 1
            if 1-(tmp_min_p / mean_price) > 0.02:
                count += 1
            tmp_start = tmp_fin
    return count

if __name__ == '__main__':
    sids = get_all_stock_id()
    bc_result = []
    for index, row in sids.iterrows():
        stock_id = row['stock_id']
        zh_name = get_zh_name(stock_id)[0][0]
        bc = count_bentou(stock_id)
        bc_result.append((stock_id, zh_name, bc))
    bc_result = sorted(bc_result, key=lambda bc_result: bc_result[2])
    for bc in bc_result:
        print('[{}][{}]-{}'.format(bc[0], bc[1], bc[2]))
