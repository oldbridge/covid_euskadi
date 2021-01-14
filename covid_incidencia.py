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
from functions import read_sample_data, get_populations, get_time_series, get_incidence_series, get_incidence_series

if __name__ == '__main__':
    municipios_url = r"https://opendata.euskadi.eus/contenidos/ds_informes_estudios/covid_19_2020/opendata/generated/covid19-bymunicipality.json"
    sample_data = "sample_data/covid19-bymunicipality_11012021.json"
    with open(sample_data, 'r') as f:
        datas = json.load(f)
    
    cities = ["Irun", "Hondarribia", "Usurbil", "Oiartzun"]
   
    sizes = get_populations(datas, cities)
    
    df = get_time_series(datas, cities)
    
    for city in cities:
        inci = get_incidence_series(df[city], sizes[city])
        # Plot the incidencias acumuladas
        plt.plot(inci['incidence14_100k'])
    
    # Plot decoration
    label = cities + ["LABI muga"]
    
    plt.plot(df.index, [500] * len(df.index), 'r--')
    plt.grid(True)
    plt.legend(label)
    plt.xlabel("Date")
    plt.ylabel("Incidencia acumulada en 14 días por 100000 habitantes")