# -*- coding: utf-8 -*-
"""

@author: caitlin
The strategy uses the aroon indicator to determine buy and sell signals.
The aroon up indicator shows how many periods since a 25 period high, and similarly the aroon down
indicator shows how many periods since a 25 period low. Readings range from 0 to 100. Generally the
market is bullish if aroon up > 50 and bearish if aroon down < 50.

Please note this strategy has been replaced by Aroon_solo and Aroon_adx which performed better after
backtesting.
"""

import pandas as pd
import mplfinance as mpf
import numpy as np
import ta


class AroonIndicator:

    # loading the data in from file_path
    def __init__(self, file_path):
        self.max_window = 100
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    # Calculate the aroon up line
    def calculate_aroon_up(self):
        aroon_up = ta.trend.aroon_up(close=self.close)
        self.df['aroon_up'] = aroon_up

    # Calculate the aroon down line
    def calculate_aroon_down(self):
        aroon_down = ta.trend.aroon_down(close=self.close)
        self.df['aroon_down'] = aroon_down

    def calculate_aroon_indicator(self):
        aroon_ind = ta.trend.AroonIndicator(close = self.close)
        self.df['aroon_ind'] = aroon_ind.aroon_indicator()

    def determine_signal(self):
        self.df['signal'] = 0

        # A buy entry signal is given when aroon up crosses over aroon down and aroon up > 50 and aroon down < 50
        self.df.loc[((self.df['aroon_up'] > 50) & (self.df['aroon_down'] < 50)
                     & (self.df['aroon_up'].shift(1) < self.df['aroon_down'].shift(1))
                     & (self.df['aroon_up'] > self.df['aroon_down'])), 'signal'] = 1

        # A sell entry signal is given when aroon up crosses down through aroon down and aroon down > 50 and aroon up < 50
        self.df.loc[((self.df['aroon_down'] > 50) & (self.df['aroon_up'] < 50)
                     & (self.df['aroon_down'].shift(1) < self.df['aroon_up'].shift(1))
                     & (self.df['aroon_down'] > self.df['aroon_up'])), 'signal'] = -1

        #returns buy sell or hold signal and aroon indicator: aroonup - aroondown
        signal_col = self.df.columns.get_loc('signal')
        return (self.df.iloc[-1, signal_col], self.df['aroon_ind'].iloc[-1])

    # Runs the indicator
    def run_aroon_indicator(self):
        self.calculate_aroon_up()
        self.calculate_aroon_down()
        self.calculate_aroon_indicator()
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
        plot_df.loc[sell_marker_index, 'sell_marker'] = plot_df.loc[sell_marker_index, 'high'] + plot_df.range * 0.09

    def plot_graph(self):

        # make a copy so original is unimpacted
        plot_df = self.df.copy(deep=False)

        plot_df.range = max(plot_df['high']) - min(plot_df['low'])

        line_50 = [50] * self.max_window
        # determine buy/sell marker
        self.determine_buy_marker(plot_df)
        self.determine_sell_marker(plot_df)

        # set index to datetime
        plot_df.index = pd.to_datetime(plot_df.datetime)

        # create subplots to show adx, rsi and boundary values 25, 30, 70
        apds = [
            mpf.make_addplot(plot_df['aroon_up'], panel=1, color='g', ylabel='aroon up \n(green)'),
            mpf.make_addplot(plot_df['aroon_down'], panel=1, color='m', ylabel='aroon down \n(pink)'),
            mpf.make_addplot(line_50, panel=1, color='k')
        ]

        # if current subset of data has a buy/sell example, add to plot
        if not plot_df['buy_marker'].isnull().all():
            apds.append(mpf.make_addplot(plot_df['buy_marker'], type="scatter", marker="^", markersize=60, color="green"))
        if not plot_df['sell_marker'].isnull().all():
           apds.append(mpf.make_addplot(plot_df['sell_marker'], type = "scatter", marker="v", markersize = 60, color="red"))

        # Create colour style candlestick colours to green and red
        mc = mpf.make_marketcolors(up='g', down='r')
        # set colour and grid style
        s = mpf.make_mpf_style(marketcolors=mc)
        # view plot
        mpf.plot(plot_df, type="candle", addplot=apds, figscale = 1, style=s, title="Aroon Indicator Strategy")




