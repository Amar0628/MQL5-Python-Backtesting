import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:
https://www.ig.com/au/trading-strategies/macd-trading-strategy-190610#histogramreversals
'''

class MACDHistogramReversal:

    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        #self.df = pd.DataFrame(file_path)

    def add_macd_line(self):
        self.df['macd_line'] = ta.trend.MACD(close = self.df['close']).macd()

    def add_macd_signal_line(self):
        self.df['macd_signal'] = ta.trend.MACD(close = self.df['close']).macd_signal()

    def add_macd_diff(self):
        self.df['macd_histogram'] = ta.trend.MACD(close = self.df['close']).macd_diff()

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0

        #BUY MACD histogram is reversing up
        if((dframe['macd_histogram'].iloc[-1] > dframe['macd_histogram'].iloc[-2]) &
           (dframe['macd_histogram'].iloc[-2] > dframe['macd_histogram'].iloc[-3]) &
           (dframe['macd_histogram'].iloc[-3] < dframe['macd_histogram'].iloc[-4]) &
           (dframe['macd_histogram'].iloc[-4] < dframe['macd_histogram'].iloc[-5])):

           signal = 1

        #SELL if MACD histogram is reversing down
        if((dframe['macd_histogram'].iloc[-1] < dframe['macd_histogram'].iloc[-2]) &
           (dframe['macd_histogram'].iloc[-2] < dframe['macd_histogram'].iloc[-3]) &
           (dframe['macd_histogram'].iloc[-3] > dframe['macd_histogram'].iloc[-4]) &
           (dframe['macd_histogram'].iloc[-4] > dframe['macd_histogram'].iloc[-5])):

           signal = -1

        return signal

    # determine and return additional useful information
    def determine_additional_info(self, dframe):

        return dframe.iloc[-1]['macd_histogram'] - dframe.iloc[-1]['close']

    def run_macd_histogram_reversal(self):

        # perform calculations
        self.add_macd_line()
        self.add_macd_signal_line()
        self.add_macd_diff()

        # generate data for return tuple
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
        visualisation.add_subplot(plot_df['macd_signal'], panel=1, color='b', width=0.75, ylabel='MACD signal\n(blue)')
        visualisation.add_subplot(plot_df['macd_histogram'], panel=2, color='r', type = 'bar', width=0.75, ylabel='Histogram\n(red)')


        # create final plot with title
        visualisation.plot_graph("MACD Histogram Reversal Strategy")
