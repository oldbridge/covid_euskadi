# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 19:19:07 2021

@author: Xabi
"""


from functions import load_from_file, get_populations, get_time_series, get_incidence_series


import numpy as np
import matplotlib.pyplot as plt
import pandas
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=5):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back)]
		dataX.append(a)
		dataY.append(dataset[i + look_back])
	return np.array(dataX), np.array(dataY)

if __name__ == '__main__':
    filename = 'download/covid19-bymunicipality.json'
    
    cities = ["Irun"]
    
    datas = load_from_file(filename)
    
    sizes = get_populations(datas, cities)
    
    df = get_time_series(datas, cities)
    
    train_len = 0.6
    verify_len = 0.4
    look_back = 5
    
    for city in cities:
        inci = get_incidence_series(df[city], sizes[city])
        inci_np = np.array(inci['incidence14_100k'])[14:]
        # Plot the incidencias acumuladas
        
        
        # normalize the dataset
        inci_np = inci_np / max(inci_np)
        
        #plt.plot(inci_np, '-o')
        
        # Split the data
        training_data = inci_np[:int(len(inci_np) * train_len)]
        verify_data = inci_np[int(len(inci_np) * train_len):int(len(inci_np) * train_len) + int(len(inci_np) * verify_len)]
        
        # Create train dataset
        trainX, trainY = create_dataset(training_data)
        verifyX, verifyY = create_dataset(verify_data)
        
        # reshape input to be [samples, time steps, features]
        trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
        verifyX = np.reshape(verifyX, (verifyX.shape[0], 1, verifyX.shape[1]))
        
        # create and fit the LSTM network
        model = Sequential()
        model.add(LSTM(4, input_shape=(1, look_back)))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)
        
        # Plot training data + prediction
        predY = model.predict(verifyX)
        plt.plot(verifyY)
        plt.plot(predY)
        
        plt.legend(['Real', 'Prediction'])
        
        