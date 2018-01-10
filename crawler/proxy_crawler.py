import sys, os
if (sys.version_info > (3, 0)): 
    import pymysql as mysql
    from lib.mylogger import MyLogger
else:
    import MySQLdb as mysql
    from mylogger import MyLogger

import ipdb 
from lxml import etree
import requests

from settings import *

class ProxyCrawler(object):
    _headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    _timeout = 60
    _proxy = []
    _anonimity = {
        'transparent': 0,
        'elite proxy': 1,
        'anonymous': 2
    }
    _proxy_list_website = [
        'https://free-proxy-list.net/',
        'https://www.sslproxies.org/'
    ]

    def __init__(self):
        self.mysql = mysql.connect(HOST, USER, PASSWORD, 'proxy_server')
        self.session = requests.Session()
        self.logger = MyLogger(name='proxy', prefix='proxy')

    def run(self):
        for website in self._proxy_list_website:
            self.fetch_proxy(website)

    def get(self, url):
        try:
            #response = self.session.get(url, headers=self._headers, timeout=self._timeout)
            response = requests.get(url, timeout=self._timeout)
        except requests.exceptions.ReadTimeout:
            self.logger.debug('[!] timeout')
            print('[-] requests timeout.')
        return response

    def fetch_proxy(self, website):
        response = self.get(website)
        tree = etree.HTML(response.content)
        proxy_elements = tree.xpath('.//tr')
        cursor = self.mysql.cursor()
        for element in proxy_elements[1:]:
           proxy_info = [child.text for child in element.getchildren()[:-1]]
           try:
               proxy_info[4] = self._anonimity[proxy_info[4]] 
           except:
               continue
           if proxy_info[5] == 'yes':
               proxy_info[5] = 1
           else:
               proxy_info[5] = 0
           if proxy_info[6] == 'yes':
               proxy_info[6] = 1
           else:
               proxy_info[6] = 0
           try:
               cursor.execute('insert ignore into `ssl_proxy` (`ip`, `port`, `code`, `country`, `anonimity`, `google`, `https`, `last_check`) values (INET6_ATON(%s), %s, %s, %s, %s, %s, %s, now())', proxy_info)
               self.logger.info('[+] {}'.format(proxy_info))
           except Exception as e:
               self.logger.warning('[-] {}'.format(proxy_info))
               continue
        self.mysql.commit()
        cursor.close()

if __name__ == '__main__':
    crawler =  ProxyCrawler()
    crawler.run()
