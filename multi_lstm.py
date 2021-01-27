# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 19:03:07 2021

@author: Xabi
"""

from functions import read_from_csv_net, read_populations
import matplotlib.pyplot as plt
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

if __name__ == '__main__':
    df = read_from_csv_net()
    cities = df['municipios'].columns[:-1].to_list()
    sizes = read_populations()
    
    # Filter only more than 5000 ppl cities
    
    sizes = sizes[sizes['inhabitants'] > 5000]
    
    cities = sizes.index.to_list()
    
    # Prepare the data and plot if needed
    # Aim is to input a ([t-5, t] days x n_cities) array
    # and output a ([t + 1, t + 3 x 1]) array for a choosen city
    # By Keras standard reshape input to be 3D [samples, timesteps, features]
    
    dataX = np.zeros(shape=(len(df['municipios']), len(cities)))
    dataY = np.zeros(shape = (len(df['municipios']), 1))
    
    plot = True
    i = 0
    pred_city = "Tolosa"
    pred_i = cities.index(pred_city)
    predict_days = 5 # Try to forecast 5 days in future
    
    for city in cities:
        incidencia = df['municipios'][city].rolling(14).sum() * 100000 / int(sizes[sizes.index == city]['inhabitants'])
        
        if plot:
            plt.plot(incidencia) 
        # Normalize by 3000 (never an incidence higher than 3000)
        incidencia = incidencia / 3000
        
        # Fill na values with 0
        incidencia = incidencia.fillna(0)
        
        # Turn into a numpy array
        incidencia = incidencia.to_numpy()
        
        # Add to array
        dataX[:, i] = incidencia
        
        # Add predicted value
        if city == pred_city:
            dataY = np.roll(incidencia, -predict_days)
        i += 1
     
    
    if plot:
        plt.grid(True)
        plt.legend(cities)
        
    # Reshape the arrays for Keras input
    dataX = dataX.reshape(dataX.shape[0], 1, dataX.shape[1])
    dataY = dataY.reshape(dataY.shape[0], 1, 1)
    
    # Divide data
    train_days = 150
    trainX = dataX[:train_days, :, :]
    trainY = dataY[:train_days, :, :]
    
    # This is my network
    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(50, input_shape=(trainX.shape[1], trainX.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)
    
    predY = model.predict(dataX)
    
    # Plot results
    plt.plot(dataX[:, :, pred_i].reshape((dataX.shape[0])))
    plt.plot(dataY.reshape((dataY.shape[0])))
    plt.plot(predY.reshape((predY.shape[0])))
    plt.plot([train_days, train_days], [0,np.max(dataX[:,:, pred_i])],  'r--')
    
    plt.legend(["Input data", "Real future data", "Predicted future data", "Train boundary"])
    plt.grid(True)
    plt.ylabel("Incidencia 14 dias por 100k habitantes (normalizado /3000)")
    plt.xlabel("Days since data begin")
    plt.title(f"{predict_days} in the future forecast for {pred_city}, LSTM 4 neurons, trained for {train_days} days")
    
    