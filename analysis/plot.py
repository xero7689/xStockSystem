# -*- coding:utf-8 -*-

import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
import pandas as pd
from lib.mysql import get_all_stock_info, get_zh_name
from settings import chinese_font_path

# Color Scheme
FACE_COLOR = '#F1EFE2'
EDGE_COLOR = '#E7E4D3'
GRID_COLOR = '#C0C0C0'

#fig, ax = plt.subplots(figsize=(15, 7))
ax = plt.subplot2grid((7,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
font = FontProperties(fname=chinese_font_path)

sid = sys.argv[1]
sid = int(sid)
df = get_all_stock_info(sid)
zh_name = get_zh_name(sid)[0][0]

# Transform `date` field and setting as index
df['date'] = pd.to_datetime(df['date'])
df = df.set_index(pd.DatetimeIndex(df['date']))
df = df.sort_index()

# Mask to limit the plot range
mask = df['date'] > '2017-12-01'
ddf = df[mask]

# Set xaxis
ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%y %b %d'))

# Plot
ax.plot(ddf['date'], ddf['price'])
ax.plot(ddf['date'], ddf['price'].rolling(window=7).mean(), color='#FFD700', linewidth=0.7, ls='--')
ax.plot(ddf['date'], ddf['price'].rolling(window=14).mean(), color='#FFA500', linewidth=0.7, ls='--')
ax.plot(ddf['date'], ddf['price'].rolling(window=28).mean(), color='#FF8C00', linewidth=0.7, ls='--')
t = pd.Timestamp('2018-01-29')

# Plot stick
# The dataframe needs to be reshape and turn from Timestamp to numpy.int64
ddfreshape = ddf.reindex(columns=['date', 'op', 'max', 'min', 'price', 'lot', 'pe', 'yield'])
ddfreshape['date'] = ddfreshape['date'].apply(mdates.date2num).apply(np.int64)
candlestick_ohlc(ax, ddfreshape.values, width=0.6, colorup='#DC143C', colordown='#2E8B57')

# Plot vol
axv = ax.twinx()
axv.fill_between(ddfreshape['date'].values, 0, ddfreshape['lot'].values, facecolor=FACE_COLOR, alpha=.4)
axv.set_ylim(0, max(3*ddfreshape['lot'].values))
axv.axes.yaxis.set_ticklabels([])
axv.grid(False)

# AX-PE
axpe = plt.subplot2grid((7,4), (0,0), sharex=ax, rowspan=1, colspan=4, axisbg=FACE_COLOR)
axpe.plot(ddf['date'], ddf['pe'], color='#206BA4')
mean_pe = ddf['pe'].mean()
axpe.axhline(y=mean_pe, linewidth='0.6', color='#D8BFD8', ls='--')
#axpe.set_ylim(min(ddf['pe']), max(ddf['pe']))
axpe.legend(['PE'], prop=font)
axpe.set_ylabel('PE')

# AX-BIAS
axbias = plt.subplot2grid((7,4), (5,0), sharex=ax, rowspan=1, colspan=4, axisbg='#F1EFE2')
ma_7 = ddf['price'].rolling(window=7).mean()
sp = len(ddf['price']) - len(ma_7)
rsi = (ddf['price'][sp:] - ma_7[sp:])/(ma_7[sp:])
axbias.plot(ddf['date'], rsi, color='#206BA4')
axbias.axhline(y=0.0, linewidth='0.6', color='red', ls='--')
axbias.legend(['乖離率'], prop=font)

# Some plt settings

ax.patch.set_facecolor(FACE_COLOR)
ax.patch.set_edgecolor(EDGE_COLOR)
ax.grid(color=GRID_COLOR)
axpe.grid(color=GRID_COLOR)
axbias.grid(color=GRID_COLOR)
ax.legend(['股價', '7日均線', '14日均線', '28日均線'], prop=font)
ax.set_ylabel('Price')
axv.set_ylabel('Vol')
start_date = (ddf['date'][ddf.index[0]]).strftime('%Y-%m-%d')
end_date = (ddf['date'][ddf.index[-1]]).strftime('%Y-%m-%d')
axpe.set_title('[{}] {} {}~{}'.format(sid, zh_name, start_date, end_date), fontproperties=font)
plt.setp(ax.get_xticklabels(), visible=False, rotation=65)
plt.setp(axpe.get_xticklabels(), visible=False, rotation=65)
plt.setp(axbias.get_xticklabels(), visible=True, rotation=65)
plt.savefig("test.png",bbox_inches='tight')
plt.show()
