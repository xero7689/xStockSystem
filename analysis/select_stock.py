from itertools import combinations
from lib.mysql import get_all_stock_id

def make_stock_combination():
    all_id = get_all_stock_id()
    all_id = all_id['stock_id'].values.tolist()
    return list(combinations(all_id, 2))
