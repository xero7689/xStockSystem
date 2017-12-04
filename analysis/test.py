import pymysql
import pandas as pd

if __name__ == '__main__':
    db = pymysql.connect('localhost', 'xero', 'uscrfycn', 'taiwan_stock')
    df = pd.read_sql('select date, price, yield from daily where stock_id = 1101;', con=db)
    print(df)
    df['date'] = pd.to_datetime(df['date'])
    b = df['date'].dt
    print(df.groupby([b.year])['price'].mean())
    print(df.groupby([b.year])['price'].std())
