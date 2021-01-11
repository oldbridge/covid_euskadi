# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 18:25:27 2021

@author: Xabi
"""


import json
import requests
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timezone

def read_sample_data():
    sample_data = "sample_data/covid19-bymunicipality_11012021.json"
    with open(sample_data, 'r') as f:
        datas = json.load(f)
    return datas

def get_populations(datas, cities):
    sizes = {}
    # Get population of target cities
    for data in datas['byMunicipalityByDate']['populationByMunicipalityByDate']:
        city = data['dimension']['officialName']
        if city in cities:
            sizes[city] = data['values'][0]
    return sizes

def get_time_series(datas, cities):
    
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
    return df

def get_all_data(datas):
    df = pd.DataFrame()
    for data in datas['newPositivesByDateByMunicipality']:
        date = data['date']
        entry = {'date': date}
        for i in data['items']:
            count = i['positiveCount']
            city = i['geoMunicipality']['officialName']
            entry[city] = count
        df = df.append(entry, ignore_index=True)
    df['date'] = pd.to_datetime(df['date'])
    
    # Arreglar cagada de OpenData
    for i, row in df.iterrows():
        if (row['date'] <= datetime(2021, 12, 31, tzinfo=timezone.utc)) & (row['date'] > datetime(2021, 4, 1, tzinfo=timezone.utc)):
            row['date'] = row['date'].replace(year=2020)
            df.iloc[i] = row
    
    df.set_index("date", inplace=True)
    return df

def calculate_incidences(df, cities, sizes):
    # Calcula incidencias acumuladas
    processed = pd.DataFrame()
    for city in cities:
        filt_df = df[df['city'] == city]
        filt_df['incidencia7_abs'] = filt_df.rolling(7).sum()
        filt_df['incidencia7_100k'] = filt_df['incidencia7_abs'] * 100000 / sizes[city]
        processed = processed.append(filt_df)
    
    return processed