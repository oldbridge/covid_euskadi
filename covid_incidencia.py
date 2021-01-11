# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 16:01:25 2021

@author: Xabier
"""

import json
import requests
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timezone
from functions import read_sample_data, get_populations, get_time_series, calculate_incidences

if __name__ == '__main__':
    municipios_url = r"https://opendata.euskadi.eus/contenidos/ds_informes_estudios/covid_19_2020/opendata/generated/covid19-bymunicipality.json"
    sample_data = "sample_data/covid19-bymunicipality_11012021.json"
    with open(sample_data, 'r') as f:
        datas = json.load(f)
    
    cities = ["Irun", "Hondarribia", "Aizarnazabal"]
   
    sizes = get_populations(datas)
    
    df = get_time_series(datas, cities)
    
    processed = calculate_incidences(df, cities, sizes)
    # Plot the incidencias acumuladas
    for city in cities:
        filt_df = processed[processed['city'] == city]
        plt.plot(filt_df['incidencia7_100k'])
    
    # Plot decoration
    label = cities + ["LABI muga"]
    
    plt.plot(filt_df.index, [500] * len(filt_df), 'r--')
    plt.grid(True)
    plt.legend(label)
    plt.xlabel("Date")
    plt.ylabel("Incidencia acumulada en 7 días por 100000 habitantes")