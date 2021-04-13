# -*- coding: utf-8 -*-

import pandas as pd
import mplfinance as mpf
import ta
import numpy as np
import trading_strategies.visualise as v


file_path = r"C:\Uni\2020 Sem 2\INFO3600 Group Work\unit_tests\inputs\200_periods_in.csv"

class MFI:
    def __init__(self, file_path):
        #self.df = pd.read_csv(file_path)
        self.df = pd.DataFrame(file_path)
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']
        self.volume = self.df['vol']

    def calculate_mfi(self):
        self.df['mfi'] = ta.volume.MFIIndicator(high = self.high, low = self.low, close = self.close, volume = self.volume).money_flow_index() # n is left at the default of 14

    def determine_signal(self):

        #initialise all signals to hold: 0
        self.df['signal'] = 0

        #BUY SIGNAL: when mfi was in oversold zone of below 20 and crosses above 20, the bearish market is ready to return to normal
        self.df.loc[(self.df['mfi'] > 20) & (self.df['mfi'].shift(1) <= 20), 'signal'] = 1

        #SELL SIGNAL: when mfi was in overbought zone of above 80 and crosses below 80, the bullish market is ready to return to normal
        self.df.loc[(self.df['mfi'] < 80) & (self.df['mfi'].shift(1) >= 80), 'signal'] = -1

        #return final data point's signal
        return(self.df['signal'].iloc[-1])

    def run(self):
        self.calculate_mfi()
        signal = self.determine_signal()
        return (signal, self.df['mfi'].iloc[-1])

    ''' The following methods are for plotting '''

    def determine_buy_marker(self, plot_df):
        plot_df['buy_marker'] = np.nan
        # get index of first buy example in input dataset
        buy_index_ls = plot_df.index[(plot_df['signal'] == 1)].tolist()
        # if a buy example exists
        if buy_index_ls:
            buy_marker_index = buy_index_ls[0]
            # set buy marker value to a little lower than other graph elements (for visual purposes)
            plot_df.loc[buy_marker_index, 'buy_marker'] = plot_df.loc[buy_marker_index, 'low'] - plot_df.range * 0.1

    def determine_sell_marker(self, plot_df):
        plot_df['sell_marker'] = np.nan
        # get index of first sell example in input dataset
        sell_index_ls = plot_df.index[(plot_df['signal'] == -1)].tolist()
        # if sell example exists
        if sell_index_ls:
            sell_marker_index = sell_index_ls[0]
            # set sell marker value to a little higher than other graph elements (for visual purposes)
            plot_df.loc[sell_marker_index, 'sell_marker'] = plot_df.loc[
                                                                sell_marker_index, 'high'] + plot_df.range * 0.1

    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)
        plot_df = plot_df
        plot_df.range = max(plot_df['high']) - min(plot_df['low'])
        # determine buy and/or sell marker
        self.determine_buy_marker(plot_df)
        self.determine_sell_marker(plot_df)

        # set index to datetime
        plot_df.index = pd.to_datetime(plot_df.datetime)
        # Create colour style colours to green and red
        mc = mpf.make_marketcolors(up='g', down='r')

        line_20 = self.df['signal'].size * [20]
        line_80 = self.df['signal'].size * [80]

        apds = [
            mpf.make_addplot((plot_df['mfi']), panel=1, color='m', width=0.75, ylabel='MFI'),
            mpf.make_addplot(line_20, panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid'),
            mpf.make_addplot(line_80, panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')
        ]

        # if current subset of data has a buy/sell example, add to plot
        if not plot_df['buy_marker'].isnull().all():
            apds.append(
                mpf.make_addplot(plot_df['buy_marker'], type="scatter", marker="^", markersize=60, color="green"))
        if not plot_df['sell_marker'].isnull().all():
            apds.append(
                mpf.make_addplot(plot_df['sell_marker'], type="scatter", marker="v", markersize=60, color="red"))

        # Set colour and grid style
        s = mpf.make_mpf_style(marketcolors=mc)
        mpf.plot(plot_df, type='candle', style=s, addplot=apds, title="\nMFI Strategy")

#strategy = MFI(file_path)
#signal = strategy.run_mfi()
#print(strategy.plot_graph())
