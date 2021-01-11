# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 18:25:11 2021

@author: Xabi
"""


import json
import requests
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timezone
from functions import read_sample_data, get_populations, get_all_data

if __name__ == '__main__':
    datas = read_sample_data()
    
    df = get_all_data(datas)
    sizes = get_populations(datas, df.columns)
    
    # Get the 7 day aggregate positive cases
    incidencias7_abs = df.rolling(7).sum()
    
    # Use only municipalities with enough inhabitants for statistical significance
    min_pop = 1000
    
    # Get the 7 day aggregate positive cases per 100 000 inhabitants
    incidencias7_100k = pd.DataFrame()
    for city in incidencias7_abs:
        try:
            pop = sizes[city]
            if pop > min_pop:
                incidencias7_100k[city] = incidencias7_abs[city] * 100000 / pop
        except KeyError:
            pass
    
    corrs = pd.DataFrame()
    
    # Correlate all with all
    for city_a in incidencias7_100k:
        entry = {'city_a': city_a}
        for city_b in incidencias7_100k:
            corr = df[city_a].corr(df[city_b])
            #print(city_a, city_b, corr)
            entry[city_b] = corr
        corrs = corrs.append(entry, ignore_index=True)
    
    corrs.set_index('city_a', inplace=True)
    
    # Search highly correlated cities
    corr_high = 0.70
    for city in corrs:
        coincidences = list(corrs[corrs[city] > corr_high].index)
        coincidences.remove(city)
        if coincidences:
            print(city, coincidences)
                            
            