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

if __name__ == '__main__':
    municipios_url = r"https://opendata.euskadi.eus/contenidos/ds_informes_estudios/covid_19_2020/opendata/generated/covid19-bymunicipality.json"
    
    resp = requests.get(url=municipios_url)
    datas = resp.json() # Check the JSON Response Content documentation below
    
    cities = ["Irun", "Hondarribia"]
    sizes = {}
   
    
    # Get population of target cities
    for data in datas['byMunicipalityByDate']['populationByMunicipalityByDate']:
        city = data['dimension']['officialName']
        if city in cities:
            sizes[city] = data['values'][0]
    
    df = pd.DataFrame()
    for data in datas['newPositivesByDateByMunicipality']:
        date = data['date']
        for i in data['items']:
            count = i['positiveCount']
            city = i['geoMunicipality']['officialName']
            if city in cities:
                df = df.append({'city': city, 
                                'date': date, 
                                'count': count}, ignore_index=True)
    
    df['date'] = pd.to_datetime(df['date'])
    # Arreglar cagada de OpenData
    for i, row in df.iterrows():
        if (row['date'] <= datetime(2021, 12, 31, tzinfo=timezone.utc)) & (row['date'] > datetime(2021, 4, 1, tzinfo=timezone.utc)):
            row['date'] = row['date'].replace(year=2020)
            df.iloc[i] = row
    
    df.set_index("date", inplace=True)
    # Calcula incidencias acumuladas
    processed = pd.DataFrame()
    for city in cities:
        filt_df = df[df['city'] == city]
        filt_df['incidencia7_abs'] = filt_df.rolling(7).sum()
        filt_df['incidencia7_100k'] = filt_df['incidencia7_abs'] * 100000 / sizes[city]
        processed = processed.append(filt_df)
        

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