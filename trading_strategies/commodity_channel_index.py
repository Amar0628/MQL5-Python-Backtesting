# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 12:58:56 2020

@author: mingyu and caitlin

This strategy uses the CCI (Commodity Channel Index) to determine buy/sell signals. The CCI is a momentum based oscillator used for determining overbought
and oversold conditions.
"""

import pandas as pd
import ta
import trading_strategies.visualise as v


class CommodityChannelIndex:

    # loading the data in from file_path
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    # calculates the cci
    def calculate_cci(self):
        self.df['cci'] = ta.trend.CCIIndicator(high=self.high, low=self.low, close=self.close).cci()

    # determine when to output buy/sell or hold signal
    def determine_signal(self, dframe):

        # initialise all signals to hold: 0
        signal = 0

        # A buy entry signal is given when the cci leaves the oversold zone, i.e. just above -100
        if dframe['cci'].iloc[-1] > -100 and dframe['cci'].iloc[-2] <= -100:
            signal = 1
        # A sell entry signal is given when the cci leaves the overbought zone, i.e. just above 100
        elif dframe['cci'].iloc[-1] < 100 and dframe['cci'].iloc[-2] >= 100:
            signal = -1

        return (signal, dframe['close'].iloc[-1])

    # Runs the commodity channel index strategy
    def run(self):
        self.calculate_cci()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''


    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 21  # where the current window will stop (exclusive of the element at this index)

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
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-21:])[0]

    def plot_graph(self):

        # deep copy of data so original is not impacted
        plot_df = self.df.copy(deep=True)

        # determine all signals for the dataset
        self.find_all_signals(plot_df)

        plot_df['zero_line'] = 0
        plot_df['100_line'] = 100
        plot_df['-100_line'] = -100

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of senkou span A and B to form the ichimoku cloud, and the parabolic sar dots
        visualisation.add_subplot(plot_df['cci'], panel=1, color='m', width=0.75, ylabel='CCI')
        visualisation.add_subplot(plot_df['100_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')
        visualisation.add_subplot(plot_df['-100_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')

        # create final plot with title
        visualisation.plot_graph("Commodity Channel Index Strategy")
