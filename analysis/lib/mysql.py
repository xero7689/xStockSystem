import pymysql
import pandas as pd

db = pymysql.connect('localhost', 'xero', 'uscrfycn7689', 'taiwan_stock', charset='utf8')

def get_all_stock_id():
    sql = """
        select distinct stock_id from daily;
    """
    df = pd.read_sql(sql, con=db)
    return df

def get_stock_info(sid):
    sql = """
        select date, price, yield from daily where stock_id = {};
    """.format(sid)
    df = pd.read_sql(sql, con=db)
    return df

def get_zh_name(sid):
    sql = """
        select zh_name from stock_list where stock_id = %s;
    """
    cursor = db.cursor()
    cursor.execute(sql, (sid,))
    data = cursor.fetchall()
    cursor.close()
    return data

if __name__ == '__main__':
    df = get_stock_info(1101)
    print(df)
    df['date'] = pd.to_datetime(df['date'])
    b = df['date'].dt
    print(df.groupby([b.year])['price'].mean())
    print(df.groupby([b.year])['price'].std())
    print(get_all_stock_id())
    print(get_zh_name(1101))
