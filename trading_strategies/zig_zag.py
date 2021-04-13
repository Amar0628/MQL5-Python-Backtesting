import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:
https://www.investopedia.com/terms/z/zig_zag_indicator.asp

Self-implemented.

'''

class ZigZag:

    # constructor
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        #self.df = pd.DataFrame(file_path)

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0
        
        #BUY if higher highs and higher lows (against a 10 period backdrop)
        if((dframe['high'].iloc[-10:-1].max() > dframe['high'].iloc[-20:-11].max()) &
           (dframe['low'].iloc[-10:-1].min() > dframe['low'].iloc[-20:-11].min())):
            signal = 1

        #SELL if lower highers and lower lows
        if((dframe['high'].iloc[-10:-1].max() < dframe['high'].iloc[-20:-11].max()) &
           (dframe['low'].iloc[-10:-1].min() < dframe['low'].iloc[-20:-11].min())):
            signal = -1

        return signal

    # determine and return additional useful information
    def determine_additional_info(self, dframe):

        return dframe['high'].iloc[-10:-1].max() - dframe['high'].iloc[-20:-11].max()

    # run strategy
    def run_zigzag(self):

        # generate data for return tuple
        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        # create return tuple and append data
        result = []
        result.append(signal)
        result.append(additional_info)

        return tuple(result), self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 60  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

            # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-60:])

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

        # create final plot with title
        visualisation.plot_graph("Zig Zag Trading Strategy")
