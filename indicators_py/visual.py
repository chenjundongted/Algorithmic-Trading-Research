#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 22:58:00 2022

@author: djogem
"""

# loading the class data from the package pandas_datareader f
from pandas_datareader import data 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt


def ema(num_periods, close_prices):
    num_periods = num_periods
    K = 2/(num_periods+1)
    
    ema_p = 0
    ema_values = []
    
    for close_price in close_prices:
        if (ema_p == 0): # first observation, EMA = current-price    
            ema_p = close_price 
        else:
            ema_p = (close_price - ema_p) * K + ema_p
            
        ema_values.append(ema_p)
    return ema_values

def sma(num_periods, close_prices):
    time_periods = num_periods
    history = []
    sma_values = []
    
    for close_price in close_prices:
        history.append(close_price)
        if len(history) > time_periods:
            del history[0]
        sma_values.append(np.mean(history))
    return sma_values


def cci(num_periods, Data, c):    
    typical = Data['typical'].to_numpy()
    #MAD_Data = pd.Series(Data['typical'])
   
    mad = np.zeros(len(Data['typical']))
    
    for i in range(len(Data)):
        if i < num_periods:
            mad[i] = Data['typical'].mad()
        else:
            mad[i] = Data['typical'][i - num_periods:i].mad()
            
    #mad = pd.Series(mad)

    mean_typical_price = sma(num_periods, typical)
    cci = (typical - mean_typical_price) / (c * mad)
    return cci



# First day 
start_date = '2014-01-01' 
# Last day 
end_date = '2018-01-01' 
# Call the function DataReader from the class data
goog_data = data.DataReader('GOOG', 'yahoo', start_date, end_date)

# initialization
goog_data_signal = pd.DataFrame(index=goog_data.index)
goog_data_signal['price'] = goog_data['Adj Close']
goog_data_signal['daily_difference'] = goog_data_signal['price'].diff()
goog_data_signal['signal'] = 0.0 
goog_data_signal['signal'] = np.where(goog_data_signal['daily_difference'] > 0, 1.0, 0.0) 
goog_data_signal['positions'] = goog_data_signal['signal'].diff() 
goog_data_signal['low'] = goog_data['Low']
goog_data_signal['high'] = goog_data['High']
goog_data_signal['typical'] = (goog_data_signal['price']+goog_data_signal['low']+goog_data_signal['high'])/3.0
goog_data_signal['cci_20'] = cci(20, goog_data_signal, 0.015)


sma_values = sma(20, goog_data_signal['price'])
goog_data_signal['sma_20'] = sma_values
ema_values = ema(20, goog_data_signal['price'])
goog_data_signal['ema_20'] = ema_values

fig = plt.figure() 
ax1 = fig.add_subplot(111, ylabel='Google price in $')
goog_data_signal['price'].plot(ax=ax1, color='r', lw=2., legend=True)
goog_data_signal['sma_20'].plot(ax=ax1, color='g', lw=2., legend=True)
goog_data_signal['ema_20'].plot(ax=ax1, color='k', lw=2., legend=True) 
plt.show()

# Plot CCI
ax2 = plt.subplot2grid((10,1), (6,0), rowspan = 5, colspan = 3)
ax2.set_ylabel('CCI')
ax2.set_xlabel('Date')
goog_data_signal['cci_20'].plot(ax=ax2, color = 'orange', lw=2., legend=True)
ax2.axhline(200, linestyle = '--', linewidth = 1, color = 'black', label='200')
ax2.axhline(-200, linestyle = '--', linewidth = 1, color = 'black')
ax2.set_yticks((200,-200))





