import aiohttp
import asyncio
import async_timeout
import pymysql
import time
import hashlib
from lib import color_print
from settings import *

get_null_delay_proxy = '''
    SELECT id, INET6_NTOA(ip), port, country, https
    FROM ssl_proxy
    WHERE https = 0
    AND delay IS NULL
'''

get_low_delay_proxy = '''
    SELECT id, INET6_NTOA(ip), port, country, https
    FROM ssl_proxy
    WHERE https = 0
    AND delay > 0 and delay < 1
'''

# Get proxy list from mysql
con = pymysql.connect(HOST, USER, PASSWORD, 'proxy_server')
cursor = con.cursor()
cursor.execute(get_low_delay_proxy)
low_delay_proxies = list(cursor.fetchall())
cursor.execute(get_null_delay_proxy)
null_delay_proxies = list(cursor.fetchall())
cursor.close()
con.commit()
queue = asyncio.Queue()
for proxy in low_delay_proxies:
    queue.put_nowait(proxy)
for proxy in null_delay_proxies:
    queue.put_nowait(proxy)

twsec_url = 'http://www.twse.com.tw/zh/'

_update_ssl_proxy = """
    UPDATE ssl_proxy
    SET delay = %s,
    last_check = now()
    WHERE id = %s;
"""

async def profit(session, pid, ip, port, https, country):
    global con
    cursor = con.cursor()
    proxy = '{}://{}:{}'.format(https, ip, port)
    now = time.time()
    try:
        with async_timeout.timeout(5):
            async with session.get(twsec_url, proxy=proxy) as response:
                print(response.status)
                if response.status == 200:
                    delay = time.time() - now
                    cursor.execute(_update_ssl_proxy, (delay, pid))
                    prefix = color_print.make_string('[+]', 'green')
                else:
                    delay = response.status
                    cursor.execute(_update_ssl_proxy, (delay, pid))
                    prefix = color_print.make_string('[-][{}]'.format(response.status), 'red')
    except asyncio.TimeoutError as te:
        cursor.execute(_update_ssl_proxy, (9999, pid))
        prefix = color_print.make_string('[-][timeout]', 'red')
    except aiohttp.client_exceptions.ServerDisconnectedError as ce:
        cursor.execute(_update_ssl_proxy, (-1, pid))
        prefix = color_print.make_string('[-][server disconnect]', 'red')
    except aiohttp.client_exceptions.ClientProxyConnectionError as pce:
        cursor.execute(_update_ssl_proxy, (-2, pid))
        prefix = color_print.make_string('[-][client proxy connect]', 'red')
    except aiohttp.client_exceptions.ClientOSError as cose:
        # Connection reset by peers
        cursor.execute(_update_ssl_proxy, (-3, pid))
        prefix = color_print.make_string('[-][client os error]', 'red')
    except aiohttp.client_exceptions.ClientHttpProxyError as chpe:
        cursor.execute(_update_ssl_proxy, (-4, pid))
        prefix = color_print.make_string('[-][client http proxy error]', 'red')
    except aiohttp.client_exceptions.ClientResponseError as cre:
        cursor.execute(_update_ssl_proxy, (-5, pid))
        prefix = color_print.make_string('[-][client response error]', 'red')
    delay = time.time() - now

    if delay < 1:
        delay = color_print.make_string('{}'.format(delay), 'green')
    elif 5 > delay >= 1:
        delay = color_print.make_string('{}'.format(delay), 'blue')
    else:
        delay = color_print.make_string('{}'.format(delay), 'red')
    cursor.close()
    con.commit()
    print('{} {}:{}\t{}\t{}'.format(prefix, ip, port, country, delay))

async def main():
    global queue
    while not queue.empty():
        pid, ip, port, country, https = await queue.get()
        if https is 1:
            https = 'https'
        else:
            https = 'http'
        async with aiohttp.ClientSession() as session:
            print('[*] Create session: {}://{}:{}({})'.format(https, ip, port, country))
            await profit(session, pid, ip, port, https, country)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
