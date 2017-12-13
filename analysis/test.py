import sys, os
import time
from select_stock import make_stock_combination 
from analyze_stock import count_corr
from lib.mysql import get_stock_info, get_zh_name
#import pandas as pd


if __name__ == '__main__':
    stock_comb = make_stock_combination()
    for sid1, sid2 in stock_comb:
        info1 = get_stock_info(int(sid1))
        info2 = get_stock_info(int(sid2))
        corr = count_corr(info1, info2)
        if corr > 0.7:
            zh1 = get_zh_name(sid1)[0][0]
            zh2 = get_zh_name(sid2)[0][0]
            print('{}\t{}\tCorr: {}'.format(zh1, zh2, corr))
        elif corr < 0:
            zh1 = get_zh_name(sid1)[0][0]
            zh2 = get_zh_name(sid2)[0][0]
            print('{}\t{}\tCorr: {}'.format(zh1, zh2, corr))
        time.sleep(1)

