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
    def get_rank_by_date(self, before=None, after=None, limit=10, t_num=2):
        sql_prefix = """
        select sl.zh_name, sl.stock_id, my, dd, sl.stock_cate 
        from stock_list as sl 
        inner join 
            (select d.stock_id,truncate(avg(d.yield), {}) as my, d.date as dd 
             from daily as d 
        """.format(t_num)

        # Middlefix
        if before and not after:
            sql_args = (before,)
            sql_middle = """
                 where date < %s
            """
        elif after and not before:
            sql_args = (after,)
            sql_middle = """
                 where date > %s
            """
        elif before and after:
            sql_args = (before, after)
            sql_middle = """
                where date < %s
                and date > %s
            """

        # Postfix
        sql_postfix = """
             group by d.stock_id) as d 
        on d.stock_id = sl.stock_id 
        order by my 
        desc limit {};
        """.format(limit)
        sql = sql_prefix + sql_middle + sql_postfix
        print(sql)
        return (sql, sql_args)

    @commit_handle('get')
    def get_daily(self, stock_id):
        sql_args = (stock_id,)
        sql = """
        SELECT * from daily
        WHERE stock_id = %s;
        """
        return (sql, sql_args)

    @commit_handle('get')
    def get_daily_price(self, stock_id):
        sql_args = (stock_id,)
        sql = """
        SELECT date, price from daily
        WHERE stock_id = %s
        ORDER BY date;
        """
        return (sql, sql_args)
