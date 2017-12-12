#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import time
import datetime
from functools import wraps

if (sys.version_info > (3, 0)): 
    import pymysql as mysql
else:
    import MySQLdb as mysql

from .mylogger import MyLogger

def commit_handle(exec_type): 
    """ Decorator to handle database commition
    """
    def _get_con(self):
        retry_limit = 10
        while True:
            try:
                self.connect = mysql.connect(self.host,
                                                  self.user,
                                                  self.passwd,
                                                  db=self.db)
                break
            except Exception as e:
                self.logger.error(e)
                if retry_limit == 0:
                    self.logger.error(e)
                    raise e
                else:
                    retry_limit -= 1
                time.sleep(5)

    def _commit_handle(sql_func):
        @wraps(sql_func)
        def wraper(self, *args, **kwargs):
            response = None
            while True:
                try:
                    cursor = self.connect.cursor()
                    sql, sql_args = sql_func(self, *args, **kwargs)
                    if sql:
                        #self.logger.debug(sql)
                        if sql_args:
                            response = cursor.execute(sql, sql_args)
                        else:
                            response = cursor.execute(sql)
                    if exec_type == 'get':
                        response = cursor.fetchall()
                    cursor.close()
                    self.connect.commit()
                    break
                except mysql.OperationalError as moe:
                    """ Usually 'MySQLQ server has gone away.' error.
                    """
                    #print(moe)
                    self.logger.error(moe)
                    _get_con(self)
                    time.sleep(5)
                except Exception as e:
                    #print(e)
                    self.logger.error(e)
                    _get_con(self)
                    time.sleep(5)
            return response
        return wraper
    return _commit_handle

class GenerationException(Exception):
    def __init__(self,  message):
        super(Exception, self).__init__(message)

class BaseDBAdapter(object):
    def __init__(self, host, user, password, db):
        self.logger = MyLogger(name='api_db', prefix='api_db')
        self.host = host
        self.user = user
        self.passwd = password
        self.db = db
        try:
            self.connect = mysql.connect(host, user, password, db, charset='utf8')
        except Exception as e:
            self.logger.error(e)
            raise e
    
    def close_connect(self):
        if self.connect:
            self.connect.close()

class StockMySQL(BaseDBAdapter):
    def __init__(self, host, user, password, db, *args, **kwargs):
        super(StockMySQL, self).__init__(host, user, password, db)

    @commit_handle('get')
    def select_latest_date_by_sid(self, sid):
        sql_args = (sid, )
        sql = """
        SELECT MAX(date) from daily
        WHERE stock_id = %s;
        """
        return (sql, sql_args)
    

if __name__ == "__main__":
    db = StockMySQL('127.0.0.1', 'xero', 'uscrfycn', 'taiwan_stock')
    #print(db.get_daily(1101))
    print(db.select_latest_date_by_sid(1101))