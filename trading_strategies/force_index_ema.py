#https://www.daytrading.com/force-index

import pandas as pd
import mplfinance as mpf
import ta
import numpy as np

class ForceIndexEMA:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.close = self.df['close']
        self.volume = self.df['volume']

    # calculates the force index (fi) using ta library
    def calculate_force_index(self):
        self.df['fi'] = ta.volume.ForceIndexIndicator(close = self.close, volume = self.volume).force_index() # n is left at the default of 13

    # calculates the ema (ema) using ta library
    def calculate_ema(self):
        self.df['ema'] = ta.trend.EMAIndicator(close=self.close).ema_indicator()  # n is left at the default of 14

    def determine_signal(self):

        # initialise all signals to hold: 0
        self.df['signal'] = 0

        # BUY SIGNAL: when fi is above 0 and is increasing and ema is positively sloped
        self.df.loc[(self.df['fi'] > 0) & (self.df['fi'] > self.df['fi'].shift(1)) & (self.df['ema'] > self.df['ema'].shift(1)), 'signal'] = 1

        # SELL SIGNAL: when fi is below 0 and is decreasing and ema is negatively sloped
        self.df.loc[(self.df['fi'] < 0) & (self.df['fi'] < self.df['fi'].shift(1)) & (self.df['ema'] < self.df['ema'].shift(1)), 'signal'] = -1

        # return final data point's signal
        return (self.df['signal'].iloc[-1])

    def run_force_index(self):
        self.calculate_force_index()
        self.calculate_ema()

        signal = self.determine_signal()
        return (signal, self.df['fi'].iloc[-1])