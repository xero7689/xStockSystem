import sys, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
import pandas as pd
from lib.mysql import get_all_stock_info, get_zh_name


fig, ax = plt.subplots(figsize=(15, 7))
font = FontProperties(fname='/usr/share/fonts/wenquanyi/wqy-zenhei/wqy-zenhei.ttc')

sid = sys.argv[1]
sid = int(sid)
df = get_all_stock_info(sid)
zh_name = get_zh_name(sid)[0][0]

# Parse Data
df['date'] = pd.to_datetime(df['date'])
mask = df['date'] > '2018-02-01'
ddf = df[mask]

# Set xaxis
ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

# Plot
#ax.plot(ddf['date'], ddf['price'])
ax.plot(ddf['date'], ddf['price'].rolling(window=7).mean(), color='#FFD700', ls='--')
ax.plot(ddf['date'], ddf['price'].rolling(window=14).mean(), color='#FFA500', ls='--')
ax.plot(ddf['date'], ddf['price'].rolling(window=28).mean(), color='#FF8C00', ls='--')

# Plot stick
# The dataframe needs to be reshape and turn from Timestamp to numpy.int64
ddfreshape = ddf.reindex(columns=['date', 'op', 'max', 'min', 'price', 'lot'])
ddfreshape['date'] = ddfreshape['date'].apply(mdates.date2num).apply(np.int64)
candlestick_ohlc(ax, ddfreshape.values, width=0.6, colorup='#DC143C', colordown='#2E8B57')

# Plot vol
axv = ax.twinx()
axv.fill_between(ddfreshape['date'].values, 0, ddfreshape['lot'].values, facecolor='#87CEFA', alpha=.4)
axv.set_ylim(0, max(3*ddfreshape['lot'].values))
axv.axes.yaxis.set_ticklabels([])
#ax1v.grid(False)

# Some plt settings
ax.patch.set_facecolor('#0C090A')
ax.grid(color='#2B547E')
ax.legend(['7日均線', '14日均線', '28日均線'], prop=font)
ax.set_xlabel('Date')
ax.set_ylabel('Price')
axv.set_ylabel('Vol')
start_date = (ddf['date'][ddf.index[0]]).strftime('%Y-%m-%d')
end_date = (ddf['date'][ddf.index[-1]]).strftime('%Y-%m-%d')
plt.title('[{}] {} {}~{}'.format(sid, zh_name, start_date, end_date), fontproperties=font)
plt.savefig("test.png",bbox_inches='tight')
plt.show()
