# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 13:38:29 2021

@author: Xabier
"""

import csv
import requests
import zipfile
import tempfile
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime, timedelta

csv_url = r'https://opendata.euskadi.eus/contenidos/ds_informes_estudios/covid_19_2020/opendata/situacion-epidemiologica.zip'

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

df = pd.read_csv(os.path.join(tmp_dir.name, "02.csv"), 
                 sep=";", header=1, 
                 usecols=range(6), 
                 encoding='ISO-8859-1',
                 index_col=[0],
                 parse_dates=True,
                 decimal=",")
#tmp_dir.cleanup()

# Plot stuff
inci_label = 'Euskadi: 14 eguneko 100.000 biztanleko intzidentzia metatua (PCR testak) / Euskadi: Incidencia acumulada 14 días x 100.000 habitantes (test PCRs) '
inci = df[inci_label]
plt.plot(inci)
plt.grid(True)

bar_close = datetime(2020, 11, 9)
bar_open = datetime(2020, 12, 12)
bar_new_close = datetime(2021, 1, 25)
bar_predict_open = bar_new_close + (bar_open - bar_close)

predicted_same_inci = datetime(2020, 10, 24)
offset_days = datetime(2021, 1, 22) - predicted_same_inci
pred = inci[predicted_same_inci:predicted_same_inci + timedelta(days=50)]
pred.index = pred.index + pd.offsets.Day(offset_days.days)

plt.plot(pred, 'r--')
plt.plot([bar_close, bar_close], [0, 1000], 'rx-')
plt.plot([bar_open, bar_open], [0, 1000], 'gx-')
plt.plot([bar_new_close, bar_new_close], [0, 1000], 'rx-')
plt.plot([bar_predict_open, bar_predict_open], [0, 1000], 'gx--')

