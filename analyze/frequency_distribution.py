# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from random import random
import numpy as np
from db_operation import getDataFromDb
from scipy.interpolate import spline

def drawFrequencyDistribution(name, raw_data_list, field="sentiment"):
    data_list = np.array([each[field] for each in raw_data_list])
    hist_data = plt.hist(data_list, bins = 50, \
                        weights=np.zeros_like(data_list) + 1. / data_list.size, \
                                color="c", alpha=0.5)
    n, bins = hist_data[0], hist_data[1]
    
    # 拟合
    y = n 
    x = []
    length = bins.size
    i = 1
    while i < length:
        x.append((bins[i] + bins[i-1]) / 2)
        i += 1
    x = np.array(x)
    xnew = np.linspace(x.min(),x.max(),2000)
    y_smooth = spline(x, y, xnew)
    plt.plot(xnew, y_smooth, 'r', alpha=1, linewidth=1)

    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')
    plt.title('Histogram of ' + name + ' Distribution of Sentiment')
    plt.grid(True)
    plt.show()
    
if __name__ == "__main__":    
    raw_data_list = getDataFromDb({"sex": "男"}, {"_id": 0, "sentiment": 1})
    drawFrequencyDistribution("Male", raw_data_list)

    
    