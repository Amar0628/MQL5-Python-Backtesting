import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:
https://www.ig.com/au/trading-strategies/macd-trading-strategy-190610#zerocrosses
'''

class MACDZeroCross:


    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        #self.df = pd.DataFrame(file_path)

    def add_macd_line(self):
        self.df['macd_line'] = ta.trend.MACD(close = self.df['close']).macd()

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0
        
        #BUY if macd line crosses above zero
        if((dframe['macd_line'].iloc[-2] < 0) & (dframe['macd_line'].iloc[-1] > 0)):
            signal = 1

        #SELL if macd line crosses below zero
        if((dframe['macd_line'].iloc[-2] > 0) & (dframe['macd_line'].iloc[-1] < 0)):
            signal = -1

        return signal

    # determine and return additional useful information
    def determine_additional_info(self, dframe):

        return dframe.iloc[-1]['close'] - dframe.iloc[-1]['macd_line']

    def run_macd_zero_cross(self):

        #perform calculations
        self.add_macd_line()

        #generate data for return tuple
        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        #create return tuple and append data
        result = []
        result.append(signal)
        result.append(additional_info)

        return tuple(result), self.df

    ''' The following methods are for plotting '''
    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 37

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-37:])
        plot_df.loc[plot_df.index[-1], 'signal'] = action


    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)
        self.find_all_signals(plot_df)

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(plot_df['macd_line'], panel=1, color='pink', width=0.75, ylabel='MACD line\n(pink)')



        # create final plot with title
        visualisation.plot_graph("MACD Zero Cross Strategy")
