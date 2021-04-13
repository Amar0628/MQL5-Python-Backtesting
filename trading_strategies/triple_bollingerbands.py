import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:

https://www.dolphintrader.com/gbpjpy-three-bollinger-band-forex-scalping-strategy/

This is a scalping system for highly volatile currency pairs on a set of bollinger bands with different deviations

Chart Set up:
- indicators bb with deviations 2,3,4
- pref time frame: M1
- trading sessions: Euro, London, US
- preferred currency pairs: GBP/JPY

'''

class TripleBollingerBands:

    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        #self.df = pd.DataFrame(file_path)

    def add_bollinger_bands_2_dev(self):
        self.df['2bb_high_band'] = ta.volatility.bollinger_hband(self.df['close'], window = 14, window_dev = 2, fillna = False)
        self.df['2bb_low_band'] = ta.volatility.bollinger_lband(self.df['close'], window = 14, window_dev = 2, fillna = False)

    def add_bollinger_bands_3_dev(self):
        self.df['3bb_high_band'] = ta.volatility.bollinger_hband(self.df['close'], window = 14, window_dev = 3, fillna = False)
        self.df['3bb_low_band'] = ta.volatility.bollinger_lband(self.df['close'], window = 14, window_dev = 3, fillna = False)

    def add_bollinger_bands_4_dev(self):
        self.df['4bb_high_band'] = ta.volatility.bollinger_hband(self.df['close'], window = 14, window_dev = 4, fillna = False)
        self.df['4bb_low_band'] = ta.volatility.bollinger_lband(self.df['close'], window = 14, window_dev = 4,  fillna = False)

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0
        
        #BUY if price is between lower 2bb and lower 3bb
        if((dframe['close'].iloc[-1] > dframe['3bb_low_band'].iloc[-1]) &
           (dframe['close'].iloc[-1] < dframe['2bb_low_band'].iloc[-1])):
            signal = 1

        #SELL if price is between upper 2bb and upper 3bb
        if((dframe['close'].iloc[-1] > dframe['2bb_high_band'].iloc[-1]) &
          (dframe['close'].iloc[-1] < dframe['3bb_high_band'].iloc[-1])):
            signal = -1

        return signal

    # determine and return additional useful information
    def determine_additional_info(self, dframe):

        return dframe.iloc[-1]['3bb_high_band'] - dframe.iloc[-1]['3bb_low_band']

    def run_triple_bollinger_bands(self):

        #perform calculations
        self.add_bollinger_bands_2_dev()
        self.add_bollinger_bands_3_dev()
        self.add_bollinger_bands_4_dev()

        #generate data for return tuple
        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        #create return tuple and append data
        result = []
        result.append(signal)
        result.append(additional_info)

        return tuple(result)

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 200 # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-200:])

    def plot_graph(self):

        # deep copy of data so original is not impacted
        plot_df = self.df.copy(deep=True)

        # determine all signals for the dataset
        self.find_all_signals(plot_df)

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of bb and rsi
        visualisation.add_subplot(plot_df['2bb_high_band'], color="orange")
        visualisation.add_subplot(plot_df['2bb_low_band'], color="orange")
        visualisation.add_subplot(plot_df['3bb_high_band'], color="red")
        visualisation.add_subplot(plot_df['3bb_low_band'], color="red")
        visualisation.add_subplot(plot_df['4bb_high_band'], color="pink")
        visualisation.add_subplot(plot_df['4bb_low_band'], color="pink")

        # create final plot with title
        visualisation.plot_graph("Triple Bollinger Bands Strategy")
