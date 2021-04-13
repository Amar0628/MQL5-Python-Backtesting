# -*- coding: utf-8 -*-
"""

@author: mingyu and caitlin

This strategy combines the CCI, the commodity channel index with a simple moving average for 100 periods.
The CCI is a trend indicator that shows oversold and overbought conditions. Combine with the sma100
to attempt to filter some false signals.
"""

import datetime
import pandas as pd
import ta
import trading_strategies.visualise as v


class CciMovingAverage:

    # loading the data in from file_path
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    # calculates the cci
    def calculate_cci(self):
        self.df['cci'] = ta.trend.CCIIndicator(high=self.high, low=self.low, close=self.close).cci()

    # calculates the period 100 moving average
    def calculate_moving_average(self):
        self.df['average'] = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        self.df['period_100_average'] = self.df['average'].rolling(window=100).mean()


    # Runs the commodity channel index with moving average strategy
    def determine_signal(self, dframe):

        # initialise all signals to hold: 0
        signal = 0

        # A buy entry signal is when cci left oversold zone, i.e. just above -100, and price intersects the period 100 moving average from below
        if dframe['cci'].iloc[-1] > -100 and dframe['cci'].iloc[-2] <= -100 and dframe['close'].iloc[-1] > dframe['period_100_average'].iloc[-1] and dframe['close'].iloc[-2] <= dframe['period_100_average'].iloc[-2]:
            signal = 1
        # A sell entry signal is when cci left overbought zone, i.e. just below 100, and price intersects the period 100 moving average from above
        elif dframe['cci'].iloc[-1] < 100 and dframe['cci'].iloc[-2] >= 100 and dframe['close'].iloc[-1] < dframe['period_100_average'].iloc[-1] and dframe['close'].iloc[-2] >= dframe['period_100_average'].iloc[-2]:
            signal = -1

        return (signal, dframe['period_100_average'].iloc[-1])

    def run(self):
        self.calculate_cci()
        self.calculate_moving_average()
        signal = self.determine_signal(self.df)
        return signal, self.df

    '''
           the following methods are for plotting
    '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 101  # where the current window will stop (exclusive of the element at this index)

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
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-101:])[0]

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
        visualisation.add_subplot(plot_df['period_100_average'], color='red', width=1, ylabel='period100ma')
        visualisation.add_subplot(plot_df['cci'], panel=1, color='b', width=0.75, ylabel='CCI')
        visualisation.add_subplot(plot_df['100_line'], panel=1, color='k', secondary_y=False, width=0.75,
                                  linestyle='solid')
        visualisation.add_subplot(plot_df['-100_line'], panel=1, color='k', secondary_y=False, width=0.75,
                                  linestyle='solid')

        # create final plot with title
        visualisation.plot_graph("CCI MA Strategy")