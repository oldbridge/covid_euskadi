# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 19:38:05 2021

@author: Xabi
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

if __name__ == '__main__':
    sum1 = np.random.rand(400).reshape((400, 1))
    sum2 = np.random.rand(400).reshape((400, 1))
    res = sum1 + 6 ** sum2 + sum1 * sum2
    
    dataX = np.concatenate([sum1, sum2], axis=1)
    dataY = res
    
    dataX = dataX.reshape(400, 1, 2)
    dataY = dataY.reshape(400, 1, 1)
    
    trainX = dataX[:100, :, :]
    trainY = dataY[:100, :, :]
    
    # create and fit the LSTM network (for a sum lol)
    look_back = 2
    model = Sequential()
    model.add(LSTM(4, input_shape=(1, look_back)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)
    
    # Voila a LSTM able to solve sums of two numbers
    predY = model.predict(dataX)
    plt.plot(dataY.reshape((400,1)))
    plt.plot(predY)
    plt.legend(["Real", "Prediction"])
    plt.grid(True)