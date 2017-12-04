from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify

from lib.mysqlqueue import StockMySQL 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
