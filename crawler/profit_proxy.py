import aiohttp
import asyncio
import async_timeout
import pymysql
import time
import hashlib
from lib import color_print
from settings import *

# Get proxy list from mysql
con = pymysql.connect(HOST, USER, PASSWORD, 'proxy_server')
cursor = con.cursor()
cursor.execute('''
    SELECT id, INET6_NTOA(ip), port, country, https
    FROM ssl_proxy
    WHERE https = 0
    AND delay IS NULL
    ''')
proxies = list(cursor.fetchall())
cursor.close()
con.commit()
queue = asyncio.Queue()
for proxy in proxies:
    queue.put_nowait(proxy)

twsec_url = 'http://www.twse.com.tw/zh/'
async def profit(session, pid, ip, port, https, country):
    global con
    cursor = con.cursor()
    proxy = '{}://{}:{}'.format(https, ip, port)
    now = time.time()
    try:
        with async_timeout.timeout(5):
            async with session.get(twsec_url, proxy=proxy) as response:
                delay = time.time() - now
                cursor.execute("""
                               UPDATE ssl_proxy
                               SET delay = %s,
                               last_check = now()
                               WHERE id = %s;
                              """, (delay, pid))
                prefix = color_print.make_string('[+]', 'green')
    except asyncio.TimeoutError as te:
        cursor.execute("""
                       UPDATE ssl_proxy
                       SET delay = 9999,
                       last_check = now()
                       WHERE id = %s;
                      """, (pid,))
        prefix = color_print.make_string('[-]', 'red')
    except aiohttp.client_exceptions.ServerDisconnectedError as ce:
        cursor.execute("""
                       UPDATE ssl_proxy
                       SET delay = -1,
                       last_check = now()
                       WHERE id = %s;
                       """, (pid,))
        prefix = color_print.make_string('[-]', 'red')
    except aiohttp.client_exceptions.ClientProxyConnectionError as pce:
        cursor.execute("""
                       UPDATE ssl_proxy
                       SET delay = -2,
                       last_check = now()
                       WHERE id = %s;
                       """, (pid,))
        prefix = color_print.make_string('[-]', 'red')
    except aiohttp.client_exceptions.ClientOSError as cose:
        # Connection reset by peers
        cursor.execute("""
                       UPDATE ssl_proxy
                       SET delay = -3,
                       last_check = now()
                       WHERE id = %s;
                       """, (pid,))
        prefix = color_print.make_string('[-]', 'red')
    except aiohttp.client_exceptions.ClientHttpProxyError as chpe:
        cursor.execute("""
                       UPDATE ssl_proxy
                       SET delay = -4,
                       last_check = now()
                       WHERE id = %s;
                       """, (pid,))
        prefix = color_print.make_string('[-]', 'red')
    except aiohttp.client_exceptions.ClientResponseError as cre:
        cursor.execute("""
                       UPDATE ssl_proxy
                       SET delay = -5,
                       last_check = now()
                       WHERE id = %s;
                       """, (pid,))
        prefix = color_print.make_string('[-]', 'red')
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
