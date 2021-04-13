# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 12:18:14 2020

Some code snippets from pythonforfinance

@author: mingy and caitlin

This strategy uses the stochastic oscillator to determine buy and sell signals.
The indicator evaluates the market's momentum and determines overbought and oversold conditions.
"""

import pandas as pd
import mplfinance as mpf
import numpy as np
import trading_strategies.visualise as v



class StochasticOscillatorNoExit:

    def __init__(self, file_path):
        self.max_window = 50  # set to 50 for better understanding of trend in graph.
        #self.df = pd.read_csv(file_path)[-self.max_window:]
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    # Calculate the low of the 14 previous periods
    def calculate_period_14_low(self):
        self.df['period_14_low'] = self.df['low'].rolling(window=14).min()

    # Calculate the high of the 14 previous periods
    def calculate_period_14_high(self):
        self.df['period_14_high'] = self.df['high'].rolling(window=14).max()

    # Calculate the current market rate expressed as a percentage
    def calculate_current_rate(self):
        self.df['current_rate'] = 100 * ((self.df['close'] - self.df['period_14_low']) / (
                    self.df['period_14_high'] - self.df['period_14_low']))

    # Calculate the 3 period moving average of the market rate
    def calculate_period_3_average_rate(self):
        self.df['period_3_average_rate'] = self.df['current_rate'].rolling(window=3).mean()

    # determine whether to output a buy sell or hold signal
    def determine_signal(self):

        self.df['signal'] = 0

        # A buy entry signal is given when the market rate line passes up through the 3 period average line, and the market line is under 20 at that time. 
        self.df.loc[(self.df['current_rate'] < 20) & (self.df['current_rate'] >= self.df['period_3_average_rate']) & (
                    self.df['current_rate'].shift(1) < self.df['period_3_average_rate'].shift(1)), 'signal'] = 1

        # A sell entry signal is given when the market line crosses down through the 3 period average line, and the market line is above 80
        self.df.loc[(self.df['current_rate'] > 80) & (self.df['current_rate'] <= self.df['period_3_average_rate']) & (
                    self.df['current_rate'].shift(1) > self.df['period_3_average_rate'].shift(1)), 'signal'] = -1

        signal_col = self.df.columns.get_loc('signal')
        return (self.df.iloc[-1, signal_col], self.df['current_rate'].iloc[-1])

    # Runs the stochastic oscillator no exit strategy
    def run_stochastic_oscillator_no_exit(self):
        self.calculate_period_14_low()
        self.calculate_period_14_high()
        self.calculate_current_rate()
        self.calculate_period_3_average_rate()
        signal = self.determine_signal()
        return signal, self.df 

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 50  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

            # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-50:])[0]

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

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(plot_df['period_3_average_rate'], panel=1, color="orange")
        visualisation.add_subplot(plot_df['current_rate'], panel=1, color="blue")

        # create final plot with title
        visualisation.plot_graph("Stochastic Oscillator Trading Strategy")