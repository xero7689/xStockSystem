from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify

from lib.mysqlqueue import StockMySQL 
from lib.settings import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/line')
def line():
    return render_template('line.html')

@app.route('/getPrice')
def getPrice():
    response = {
        'd1': [],
        'd2': []
    }
    sid1 = request.args.get('sid1', '')
    sid2 = request.args.get('sid2', '')
    db = StockMySQL(HOST, USER, PASSWORD, 'taiwan_stock')
    d1 = db.get_daily_price(sid1)
    d2 = db.get_daily_price(sid2)
    for date, price in d1:
        tmp = {'date': date, 'price': price}
        response['d1'].append(tmp)
    for date, price in d2:
        tmp = {'date': date, 'price': price}
        response['d2'].append(tmp)
    print(jsonify(response))
    return jsonify(response)

@app.route('/mysql')
def mysql():
    db = StockMySQL('127.0.0.1', 'xero', 'uscrfycn', 'taiwan_stock')
    response = []
    data = db.get_rank_by_date(before='2017-12-01', after='2017-01-01')

    for zh_n, sid, my, dd, cate in data:
        response.append({'sid':sid, 
                         'zh': zh_n, 
                         'my':my, 
                         'date':dd, 
                         'cate':cate})
    return jsonify(response)

@app.route('/sample')
def sample():
    return render_template('sample.html')

if __name__ == "__main__":
    app.run()
