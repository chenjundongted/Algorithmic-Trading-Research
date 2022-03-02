#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 22:31:15 2022

@author: djogem
"""

import pandas as pd 
import sys
import csv
import matplotlib.pyplot as plt
import numpy as np

'''
draft: 

# read files
df = pd.read_csv('1min_AAL_211001_220101.csv')
df.set_index("<DATE>", inplace=True)
result = df.loc[["20211001"]]

# plot 
plt.plot(result["<VOL>"], result["<CLOSE>"], 'b.')


# delta
delta = 0.01
high = max(result["<HIGH>"])
low = min(result["<LOW>"])
N = int((high - low)/delta)
        
block = np.zeros(N)
close = result["<CLOSE>"].values
volume = result["<VOL>"].values
max_idx = N-1

# count into blocks
for i in range(len(close)):
    idx = min(int((close[i] - low) / delta), max_idx)
    block[idx] += volume[i]

print(block)
'''