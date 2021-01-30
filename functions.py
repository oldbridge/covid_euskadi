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
import csv
import requests
import zipfile
import tempfile
import os

def read_populations():
    filename = 'city_sizes.csv'
    sizes = pd.read_csv(filename, encoding='ISO-8859-1',index_col=[0])
    return sizes
    
def read_from_csv_net():
    csv_url = r'https://opendata.euskadi.eus/contenidos/ds_informes_estudios/covid_19_2020/opendata/situacion-epidemiologica.zip'
    
    # Filenames and data
    map_index = {'global': '01.csv',
                 'nuevos_positivos': '02.csv',
                 'sexo': '03.csv',
                 'municipios': '04.csv',
                 'positivos_zona_salud': '05.csv',
                 'muertos': '08.csv',
                 'positivos_edad': '09.csv'}
    
    # Download the data
    r = requests.get(csv_url, stream=True)
    tmp_file = tempfile.TemporaryFile(mode='w+b', suffix='.zip', delete=False)
    with open(tmp_file.name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)
    
    with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
        tmp_dir = tempfile.TemporaryDirectory()
        zip_ref.extractall(tmp_dir.name)
    
    tmp_file.close()
    
    df = {}
    for i in map_index:
        file_name = map_index[i]
        if i == 'nuevos_positivos':
            df[i] = pd.read_csv(os.path.join(tmp_dir.name, file_name), 
                             sep=";", header=1, 
                             usecols=range(6), 
                             encoding='ISO-8859-1',
                             index_col=[0],
                             parse_dates=True,
                             decimal=",")
        elif i == 'municipios':
            df[i] = pd.read_csv(os.path.join(tmp_dir.name, file_name), 
                             sep=";", header=1, 
                             encoding='ISO-8859-1',
                             index_col=[0],
                             decimal=",").transpose()[:-1]
            df[i].index = pd.to_datetime(df[i].index)
        elif i == 'global':
            df_tmp = pd.read_csv(os.path.join(tmp_dir.name, file_name), 
                             sep=";", header=1, 
                             encoding='ISO-8859-1',
                             index_col=[0],
                             decimal=",")
            
            # Only more or less usable columns
            columns = {'Testak guztira / Test totales' : "total_tests",
                       'PCR kasu positiboak / Casos positivos PCR' : "pcr_positives",
                       'ZIUn ospitaleratuak / Hospitalizados en UCI': 'uci_total',
                       'Hildakoak / Fallecidos': 'total_deaths',
                       'Ospitaleko altak / Altas hospitalarias':'hosp_release',
                       'Plantan ospitaleratuta dauden positibodunak / Ingresados en planta con positivo': 'hospital_floor',
                       ' Positibodun ospitaleratze berriak plantan / Nuevos ingresos planta con positivo': 'new_intake'}
           
            df_tmp = df_tmp.filter(items=list(columns.keys()))
            df_tmp = df_tmp.rename(columns=columns, errors='raise')
            
            # Get daily values
            df_tmp['daily_tests'] = df_tmp['total_tests'].diff()
            df_tmp['daily_positives'] = df_tmp['pcr_positives'].diff()
            
            # Interpolate deaths
            df_tmp['total_deaths'].interpolate(inplace=True)
            df_tmp['total_deaths'] = df_tmp['total_deaths'].round()
            df_tmp['daily_deaths'] = df_tmp['total_deaths'].diff()
            
            df_tmp['uci_total'].interpolate(inplace=True)
            df_tmp['uci_daily'] = df_tmp['uci_total'].diff()
            df_tmp['hosp_release'].interpolate(inplace=True)
            df_tmp['hosp_release_daily'] = df_tmp['hosp_release'].diff()
            
            # Some useful computes
            df_tmp['positivity_rate'] = df_tmp['daily_positives'] / df_tmp['daily_tests']
            
            df[i] = df_tmp
            df[i].index = pd.to_datetime(df[i].index)
    return df
    
def extend_dt_index(dt_index, num_days):
    last_day = dt_index[-1]
    for i in range(0, num_days):
        dt_index = dt_index.append(pd.DatetimeIndex([last_day + pd.DateOffset(i)]))
    return dt_index
    
def read_data_from_net(save=True, savedir="downloads"):
    municipios_url = r"https://opendata.euskadi.eus/contenidos/ds_informes_estudios/covid_19_2020/opendata/generated/covid19-bymunicipality.json"
    data = requests.get(municipios_url).json()
    if save:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        name = f'{savedir}/covid_data_{timestamp}.json'
        with open(name, 'w') as f:
            json.dump(data, f)
    return data

def load_from_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data
    
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

def get_time_series(datas, cities=None):
    """" Improved method"""
    df = pd.DataFrame(columns=cities)
    for data in datas['newPositivesByMunicipalityByDate']['positiveCountByMunicipalityByDate']:
        city = data['dimension']['officialName']
        if cities == None or city in cities:
            ts = pd.Series(data['values'], index = pd.DatetimeIndex(data['dates']))
            df[city] = ts
    
    # Arreglar cagada de OpenData
    for i, row in df.iterrows():
        if (i <= datetime(2021, 12, 31, tzinfo=timezone.utc)) & (i > datetime(2021, 4, 1, tzinfo=timezone.utc)):
            df.rename(index={i: i.replace(year=2020)}, inplace=True)
            
    return df

def get_incidence_series(ts, population):
    df = pd.DataFrame(columns=['incidence7_abs', 'incidence7_100k', 'incidence14_abs', 'incidence14_100k'])
    df['count'] = ts
    df['incidence7_abs'] = ts.rolling(7).sum()
    df['incidence14_abs'] = ts.rolling(14).sum()
    df['incidence7_100k'] = df['incidence7_abs'] * 100000 / population
    df['incidence14_100k'] = df['incidence14_abs'] * 100000 / population
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