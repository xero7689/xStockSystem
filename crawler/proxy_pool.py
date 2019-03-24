import sys, os
import itertools
from heapq import heappush, heappop
import pymysql
from settings import *

_select_proxy = """
select INET6_NTOA(ip), port, delay from ssl_proxy where delay < 5 and delay > 0;
"""

_select_proxy = """
select INET6_NTOA(ip), port, delay from ssl_proxy where delay > 0 and delay < 5 and last_check > '2018-02-01';
"""

_select_latest_low_delay_proxy = """
select INET6_NTOA(ip), port, delay from ssl_proxy where delay > 0 and delay < 5 and last_check >CURDATE();
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
        cursor.execute(_select_latest_low_delay_proxy)
        proxies = cursor.fetchall()
        for ip, port, delay in proxies:
            self.add_proxy(ip, port, delay)
        cursor.close()
        con.close()

    def get(self):
        delay, count, ip, port = self.pop_proxy()
        self.exec_proxy[(ip, port, count)] = delay
        print('--> get proxy {}'.format(ip))
        return (ip, port, delay, count)

    def release(self, ip, port, count, new_delay):
        self.exec_proxy.pop((ip, port, count))
        self.add_proxy(ip, port, new_delay)
        print('--> release proxy {} {}'.format(ip, new_delay))

    def add_proxy(self, ip, port, delay):
        count = next(self.counter)
        entry = [delay, count, ip, port]
        heappush(self.proxy_hq, entry)

    def pop_proxy(self):
        while self.proxy_hq:
            delay, count, ip, port = heappop(self.proxy_hq)
            return (delay, count, ip, port)

    def request(self, url):
        pass

if __name__ == '__main__':
    pp = ProxyPool()
    print(pp.get())

