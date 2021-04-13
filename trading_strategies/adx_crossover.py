# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 09:29:36 2020

@author: mingyu
"""

import pandas as pd
import ta
#import talib as ta
import trading_strategies.visualise as v

class AdxCrossover:
    def __init__(self, file_path):
        #self.df = pd.read_csv(file_path)
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    def calculate_adx(self):
        self.df['adx'] = ta.trend.ADXIndicator(high = self.high, low = self.low, close = self.close, window = 20).adx()

    def calculate_minus_DI(self):
        self.df['-di'] = ta.trend.ADXIndicator(high = self.high, low = self.low, close = self.close, window = 20).adx_neg()


    def calculate_plus_DI(self):
        self.df['+di'] = ta.trend.ADXIndicator(high = self.high, low = self.low, close = self.close, window = 20).adx_pos()


    def determine_signal(self, dframe):

        # initialise signal to hold: 0
        signal = 0

        # BUY SIGNAL: adx is above 25 and the positive DI crosses over negative DI indicates a strong uptrend
        if dframe['adx'].iloc[-1] > 25 and dframe['+di'].iloc[-1] > dframe['-di'].iloc[-1] and dframe['+di'].iloc[-2] <= dframe['-di'].iloc[-2]:
            signal = 1
        # SELL SIGNAL: adx is above 25 and the negative DI crosses over positive DI indicates a strong downtrend
        elif dframe['adx'].iloc[-1] > 25 and dframe['+di'].iloc[-1] < dframe['-di'].iloc[-1] and dframe['+di'].iloc[-2] >= dframe['-di'].iloc[-2]:
            signal = -1

        return (signal, dframe['close'].iloc[-1])

    def run(self):
        self.calculate_adx()
        self.calculate_minus_DI()
        self.calculate_plus_DI()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 40  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            additional_info = self.determine_signal(curr_window)[1]
            plot_df.loc[plot_df.index[end - 1], 'additional_info'] = additional_info
            end += 1
            start += 1

        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-40:])[0]

    def plot_graph(self):

        # deep copy of data so original is not impacted
        plot_df = self.df.copy(deep=True)

        # determine all signals for the dataset
        self.find_all_signals(plot_df)

        plot_df['zero_line'] = 0
        plot_df['25_line'] = 25

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of senkou span A and B to form the ichimoku cloud, and the parabolic sar dots
        visualisation.add_subplot(plot_df['adx'], panel=1, color='blue', width=0.75, ylabel='ADX')
        visualisation.add_subplot(plot_df['25_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')
        visualisation.add_subplot(plot_df['+di'], panel=1, color='green', width=0.75)
        visualisation.add_subplot(plot_df['-di'], panel=1, color='red', width=0.75)

        # create final plot with title
        visualisation.plot_graph("ADX Crossover Strategy")
