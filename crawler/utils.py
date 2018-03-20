import sys
import os
import datetime

today = datetime.datetime.today()
cur_year = today.year
cur_month = today.month
cur_day = today.day

def year_generator(start_year=2010, end_year=cur_year):
    dates = []
    for y in range(start_year, end_year+1):
        year = str(y)
        for m in range(1, 12+1):
            if (y == cur_year) and (m > cur_month):
                continue
            month = str(m)
            if m < 10:
                month = '0{}'.format(month)
            date = '{}{}01'.format(year, month)
            dates.append(date)
    return dates

def until_today_generator(start_year=2010):
    dates = []
    for y in range(start_year, datetime.datetime.now().year+1):
        year = str(y)
        for m in range(1, 12+1):
            if (y == cur_year) and (m > cur_month):
                continue
            month = str(m)
            if m < 10:
                month = '0{}'.format(month)
            date = '{}{}01'.format(year, month)
            if date < datetime.datetime.now().strftime('%Y%m%d'):
                dates.append(date)
    return dates

if __name__ == '__main__':
    for y in until_today_generator(start_year=2018):
        print(y)
