import sys, os
import itertools
from heapq import heappush, heappop
import pymysql
from settings import *

_select_proxy = """
select INET6_NTOA(ip), port, delay from ssl_proxy where delay < 5 and delay > 0;
"""

class ProxyPool(object):
    def __init__(self):
        self.proxy_hq = []
        self.exec_proxy = {}
        self.counter = itertools.count()
        self.init_hq()

    def init_hq(self):
        con = pymysql.connect(HOST, USER, PASSWORD, 'proxy_server')
        cursor = con.cursor()
        cursor.execute(_select_proxy)
        proxies = cursor.fetchall()
        for ip, port, delay in proxies:
            self.add_proxy((ip, port), delay)
        cursor.close()
        con.close()

    def add_proxy(self, proxy, delay):
        count = next(self.counter)
        entry = [delay, count, proxy]
        heappush(self.proxy_hq, entry)

    def pop_proxy(self):
        while self.proxy_hq:
            delay, count, proxy = heappop(self.proxy_hq)
            return proxy

if __name__ == '__main__':
    pp = ProxyPool()
    print(pp.pop_proxy())
    print(pp.proxy_hq)
