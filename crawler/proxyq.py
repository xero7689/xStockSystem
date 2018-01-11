import heapq
from lib.mysqlqueue import ProxyMySQL
from settings import *

class ProxyQueue:
    _queue = []
    def __init__(self):
        self.db = ProxyMySQL(HOST, USER, PASSWORD)

    def _charge(self):
        for pid, ip, port, delay in self.db.fetch():
            value = (delay, (pid, ip, port))
            heapq.heappush(self._queue, value)

    def get(self):
        if not self._queue:
            self._charge()
        return heapq.heappop(self._queue)

