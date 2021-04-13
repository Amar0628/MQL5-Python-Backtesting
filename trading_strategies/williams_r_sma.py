# -*- coding: utf-8 -*-
"""

@author: caitlin

This strategy uses the Williams%R indicator. This momentum indicator oscillates between 0 and -100, and shows
how the current price compares to a 14 day look back period, where a reading near -100 indicates the market is
near the lowest low and a reading near 0 indicates the market is near the highest high. This strategy combines
a 100 period SMA.

Please note this strategy has been replaced by Williams Stochastic or Williams RSI which were
 created as a result of backtesting and perform significantly better.
"""

import datetime
import pandas as pd
import mplfinance as mpf
import numpy as np
import ta


class WilliamsIndicator:

    # loading the data in from file_path
    def __init__(self, file_path):
        #self.max_window = 150
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))#[-self.max_window:]
        #self.df = pd.DataFrame(inputs)
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    # Calculate the williams indicator
    def calculate_williams_indicator(self):
        will_ind = ta.momentum.WilliamsRIndicator(high = self.high, low = self.low, close = self.close)
        self.df['williams_indicator'] = will_ind.wr()

    # Calculate the simple moving average
    def calculate_sma(self):
        sma_ind= ta.trend.SMAIndicator(close = self.close, window = 100)
        self.df['sma'] = sma_ind.sma_indicator()

    def determine_signal(self):
        self.df['signal'] = 0

        # A buy entry signal is given when %r line was less than -90 and now crosses up through -50 line
        # the close is greater than the sma
        self.df.loc[((self.df['williams_indicator'].shift(1) < -90) & (self.df['williams_indicator'] > -50)
                     & (self.df['close'] > self.df['sma'])), 'signal'] = 1

        # A sell entry signal is given when %r line was above -10 and now crosses down through -50 line
        # the close is less than the sma
        self.df.loc[(self.df['williams_indicator'].shift(1) > -10) & (self.df['williams_indicator'] < -50)
                    & (self.df['close'] < self.df['sma']), 'signal'] = -1

        #return buy sell or hold signal and the value of the williams indicator
        signal_col = self.df.columns.get_loc('signal')
        return (self.df.iloc[-1, signal_col], self.df['williams_indicator'].iloc[-1])

    # Runs the indicator
    def run_williams_indicator(self):
        self.calculate_williams_indicator()
        self.calculate_sma()
        signal = self.determine_signal()
        return signal, self.df

    ''' 
    the following methods are for plotting
    '''

    def determine_buy_marker(self, plot_df):
        plot_df['buy_marker'] = np.nan
        buy_index_ls = plot_df.index[(plot_df['signal'] == 1)].tolist()
        # if buy example exists
        if buy_index_ls:
            buy_marker_index = buy_index_ls[0]

        # set marker value to lower for visual purposes
        plot_df.loc[buy_marker_index, 'buy_marker'] = plot_df.loc[buy_marker_index, 'low'] - plot_df.range * 0.06

    def determine_sell_marker(self, plot_df):

        plot_df['sell_marker'] = np.nan
        sell_index_ls = plot_df.index[(plot_df['signal'] == -1)].tolist()
        # if sell example exists
        if sell_index_ls:
            sell_marker_index = sell_index_ls[0]
        # set marker value to higher for visual purposes
        plot_df.loc[sell_marker_index, 'sell_marker'] = plot_df.loc[sell_marker_index, 'high'] + plot_df.range * 0.06

    def plot_graph(self):

        # make a copy so original is unimpacted
        plot_df = self.df.copy(deep=False)

        plot_df.range = max(plot_df['high']) - min(plot_df['low'])

        # determine buy/sell marker
        self.determine_buy_marker(plot_df)
        self.determine_sell_marker(plot_df)

        # set index to datetime
        plot_df.index = pd.to_datetime(plot_df.datetime)

        line_neg90 = self.max_window * [-90]
        line_neg10 = self.max_window * [-10]
        line_neg50 = self.max_window * [-50]

        # create subplots to show williams indicator, sma and boundary lines -80 and -20
        apds = [
            mpf.make_addplot((self.df['williams_indicator']), panel=1, color='m', width=1, ylabel='williams ind'),
            mpf.make_addplot((self.df['sma']), color='k', width=1, ylabel='sma(green)'),
            mpf.make_addplot(line_neg90, panel=1, color='b', secondary_y=False, width=0.75, linestyle='solid'),
            mpf.make_addplot(line_neg10, panel=1, color='b', secondary_y=False, width=0.75, linestyle='solid'),
            mpf.make_addplot(line_neg50, panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')
        ]

        # if current subset of data has a buy/sell example, add to plot
        if not plot_df['buy_marker'].isnull().all():
            apds.append(
             mpf.make_addplot(plot_df['buy_marker'], type="scatter", marker="^", markersize=60, color="green"))
        if not plot_df['sell_marker'].isnull().all():
            apds.append(
                mpf.make_addplot(plot_df['sell_marker'], type="scatter", marker="v", markersize=60, color="red"))

        # Create colour style candlestick colours to green and red
        mc = mpf.make_marketcolors(up='g', down='r')
        # set colour and grid style
        s = mpf.make_mpf_style(marketcolors=mc)
        # view plot
        mpf.plot(plot_df, type="candle", addplot=apds, style=s, title="Williams%R Indicator Strategy")

