#! /usr/bin/python3
import pymysql


def sid_scheduler(object):
    _create = """
        CREATE TABLE IF NOT EXISTS sid_job_queue (
          stock_id varchar(255) NOT NULL,
          current_update_date date DEFAULT NULL,
          recent_schedule_date date DEFAULT NULL,
          PRIMARY KEY (sid)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    """

    _insert = """
        INSERT IGNORE INTO sid_job_queue
        (stock_id, current_update_date, recent_schedule_date)
        VALUES
        (%s, %s, %s)
    """

    _update = """
        UPDATE sid_job_queue 
        SET current_update_date = %s
        AND recent_schedule_date = %s
        WHERE sid = %s
    """

    _select = """
        SELECT stock_id FROM sid_job_queu
    """

    def __init__(self):
        self.db = pymysql.connect('localhost', 'xero', 'uscrfycn', 'taiwan_stock',
                     charset='utf8')

        # Init Job Queue Table
        cursor = self.db.cursor()
        cursor.execute(self._create)
        self.db.commit()

    def push(self, sid):
        pass

    def pop(self):
        pass


