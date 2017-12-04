import sys
import os

def year_generator(start_year=2010, end_year=2017):
    dates = []
    for y in range(start_year, end_year+1):
        year = str(y)
        for m in range(1, 12+1):
            month = str(m)
            if m < 10:
                month = '0{}'.format(month)
            date = '{}{}01'.format(year, month)
            dates.append(date)
    return dates

if __name__ == '__main__':
    for y in year_generator():
        print(y)
