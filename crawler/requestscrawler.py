#! /usr/bin/python
import sys, os
import random
import time
random.seed(time.time())

import requests
import urllib3
import ipaddress
from lxml import etree
from bs4 import BeautifulSoup

def is_valid_ip(addr):
    try:
        ipaddress.ip_address(addr)
        return True
    except ValueError:
        return False

class RequestsCrawler(object):
    _headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    _timeout = 60
    _proxy = []

    def __init__(self):
        self.session = requests.Session()
        self._update_proxy()

    def get(self, url, proxy_on=False):
        response = None
        if proxy_on:
            _ip, _port = random.choice(self._proxy)
            proxy = {'http': 'http://{}:{}'.format(_ip, _port),
                     'https': 'https://{}:{}'.format(_ip, _port),
                    }
            print(proxy)
            for i in range(5):
                try:
                    response = self.session.get(url, headers=self._headers, timeout=self._timeout, proxies=proxy)
                    break
                except requests.exceptions.ProxyError:
                    print('[-] can not make connection with proxy server')
                    self._proxy.remove((_ip, _port))
                except requests.exceptions.ReadTimeout:
                    print('[-] requests timeout.')
                    self._proxy.remove((_ip, _port))
        else:
            try:
                response = self.session.get(url, headers=self._headers, timeout=self._timeout)
            except requests.exceptions.ReadTimeout:
                print('[-] requests timeout.')
        return response

    def _update_proxy(self):
        raw_proxy_response = self.get('https://www.sslproxies.org/')
        tree = etree.HTML(raw_proxy_response.content)
        proxy_elements = tree.xpath('.//tr')
        for element in proxy_elements[1:]:
            _ip = element.getchildren()[0].text
            _port = element.getchildren()[1].text
            if _ip:
                self._proxy.append((_ip, _port))
 

if __name__ == "__main__":
    rc = RequestsCrawler()
    response = rc.get('http://www.whatismyip.com.tw/', proxy_on=True)
    print(response.content)

