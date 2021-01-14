# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 11:05:54 2021

@author: Xabier
"""

from functions import read_data_from_net, get_time_series, get_incidence_series, load_from_file, extend_dt_index
from matplotlib import pyplot as plt
import numpy as np

if __name__ == '__main__':
    filename = "downloads/covid_data_2021-01-14.json"
    #datas = read_data_from_net()
    datas = load_from_file(filename)
    df = get_time_series(datas, ['Irun'])
    inci = get_incidence_series(df['Irun'], 60000)
    
    # Plot
    fig, ax = plt.subplots(3, 1, sharex=True)
    ax[2].set_xlabel("Fecha")
    inci_14 = inci['incidence14_100k']
    # Get numpy array (omit NaN values)
    inci_np = np.array(inci_14[14:])
    
    ax[0].plot(inci_14)
    ax[0].set_ylabel("Incidencia 14d/100k")
    ax[0].grid(True)
    
    grad = np.gradient(inci_14)
    ax[1].plot(inci_14.index, grad)
    
    # Model trend using 11th order polynomial
    z = np.polyfit(range(0, len(inci_np)), inci_np, 11)
    f = np.poly1d(z)
    
    # Plot prediction over real data (Warning: Just for fun no real value!)
    future_days = 15
    new_index = extend_dt_index(inci_14[14:].index, future_days)
    
    ax[0].plot(new_index, f(range(0, len(inci_np) + future_days)))