import pymysql
import pandas as pd

db = pymysql.connect('localhost', 'xero', 'uscrfycn', 'taiwan_stock')
def get_stock_info(sid):
    sql = """
        select date, price, yield from daily where stock_id = %d;
    """ % sid
    df = pd.read_sql(sql, con=db)
    return df

if __name__ == '__main__':
    df = get_stock_info(1101)
    print(df)
    df['date'] = pd.to_datetime(df['date'])
    b = df['date'].dt
    print(df.groupby([b.year])['price'].mean())
    print(df.groupby([b.year])['price'].std())
