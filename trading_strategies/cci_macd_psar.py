# -*- coding: utf-8 -*-
"""

@author: mingyu and caitlin

This strategy combines the commodity channel index CCI with the Moving Average Convergence Divergence MACD
and Parabolic Stop and Reversal PSAR indicator. The CCI is used to show oversold and overbought zones, while
the PSAR value is checked if it is above or below the candlesticks showing a down or uptrend respectively,
 and the macd histogram is checked if it crosses the macd line from below or above indicating to buy or sell.
"""

import datetime
import pandas as pd
import ta
import trading_strategies.visualise as v

class CciMacdPsar:

    #loading the data in from file_path
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    # calculates the cci
    def calculate_cci(self):
        self.df['cci'] = ta.trend.CCIIndicator(high = self.high, low = self.low, close = self.close).cci()

    # calculates the psar
    def calculate_psar(self):
        self.df['psar'] = ta.trend.PSARIndicator(high = self.high, low = self.low, close = self.close).psar()

    # calculates the macd line
    def calculate_macd_line(self):
        self.df['macd_line'] = ta.trend.MACD(close = self.close).macd()

    # calculate the macd histogram
    def calculate_macd_histogram(self):
        self.df['macd_histogram'] = ta.trend.MACD(close = self.close).macd_diff()

    def determine_signal(self, dframe):

        # initialise all signals to hold: 0
        signal = 0

        # A buy entry signal is when cci left oversold zone, i.e. just above -100, and macd histogram crosses above the macd line and the psar is below the chart
        if dframe['cci'].iloc[-1] > -100 and dframe['cci'].iloc[-2] <= -100 and dframe['macd_histogram'].iloc[-1] > dframe['macd_line'].iloc[-1] and dframe['macd_histogram'].iloc[-2] <= dframe['macd_line'].iloc[-2] and dframe['psar'].iloc[-1] <= dframe['low'].iloc[-1]:
            signal = 1
        # A sell entry signal is when cci left overbought zone, i.e. just below 100, and macd histogram crosses below the macd line and the psar is above the chart
        elif dframe['cci'].iloc[-1] < 100 and dframe['cci'].iloc[-2] >= 100 and dframe['macd_histogram'].iloc[-1] < dframe['macd_line'].iloc[-1] and dframe['macd_histogram'].iloc[-2] >= dframe['macd_line'].iloc[-2] and dframe['psar'].iloc[-1] >= dframe['high'].iloc[-1]:
            signal = -1

        return (signal, dframe['psar'].iloc[-1])

    # Runs the commodity channel index with macd and psar indicators
    def run(self):
        self.calculate_cci()
        self.calculate_psar()
        self.calculate_macd_line()
        self.calculate_macd_histogram()
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
        end = start + 45  # where the current window will stop (exclusive of the element at this index)

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
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-45:])[0]

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
        visualisation.add_subplot(plot_df['cci'], panel=1, color='red', width=0.75, ylabel='CCI')
        visualisation.add_subplot(plot_df['100_line'], panel=1, color='k', secondary_y=False, width=0.75,
                                  linestyle='solid')
        visualisation.add_subplot(plot_df['-100_line'], panel=1, color='k', secondary_y=False, width=0.75,
                                  linestyle='solid')
        visualisation.add_subplot((self.df['macd_line']), panel=2, color='r', width=0.75, ylabel='macd line (red)'),
        visualisation.add_subplot((self.df['macd_histogram']), type="bar", panel=2, color='b', width=0.75,
                         ylabel='macd histogram'),
        visualisation.add_subplot((self.df['psar']), marker='.', type="scatter", color='m', width=0.75, ylabel='psar')

        # create final plot with title
        visualisation.plot_graph("CCI MACD PSAR Strategy")
