# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 10:19:23 2020

@author: mingy
"""

import pandas as pd
import mplfinance as mpf
import ta
import numpy as np

class MfiStochastic:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']
        self.volume = self.df['volume']

    def calculate_mfi(self):
        self.df['mfi'] = ta.volume.MFIIndicator(high = self.high, low = self.low, close = self.close, volume = self.volume).money_flow_index() #n is left at the default of 14

    def calculate_stochastic(self):
        self.df['stoch'] = ta.momentum.StochasticOscillator(high = self.high, low = self.low, close = self.close).stoch() #n is left at the default of 14
        
    def determine_signal(self):

        #initialise all signals to hold: 0
        self.df['signal'] = 0

        #BUY SIGNAL: when mfi and the stochastic indicator both leaves the oversold zone
        self.df.loc[(self.df['mfi'] > 20) & (self.df['mfi'].shift(1) <= 20) & (self.df['stoch'] > 20) & (self.df['stoch'].shift(1) <= 20), 'signal'] = 1

        #SELL SIGNAL: when mfi and the stochastic indicator both leaves the overbought zone
        self.df.loc[(self.df['mfi'] < 80) & (self.df['mfi'].shift(1) >= 80) & (self.df['stoch'] < 80) & (self.df['stoch'].shift(1) >= 80), 'signal'] = -1

        #return final data point's signal
        return(self.df['signal'].iloc[-1])

    def run_mfi_stochastic(self):
        self.calculate_mfi()
        self.calculate_stochastic()
        signal = self.determine_signal()
        return tuple(signal), self.df