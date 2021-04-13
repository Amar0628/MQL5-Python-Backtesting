# -*- coding: utf-8 -*-
"""


@author: caitlin and vita
This strategy combines 3 different indicators: MACD, RSI and SMA in order to determine buy and sell signals
The Moving Average Convergence Divergence (MACD) is a trend following momentum indicator that displays
the relation between 2 moving averages. This strategy uses the macd signal and macd line, where the signal
line trails the macd.
The Relative Strength Index (RSI) is a momentum indicator measuring speed and change of price movements.
The 5 period simple moving average is good for short term trading.
The goal of combining these indicators is to determine more accurate buy/sell signals than any provide by themselves.
"""

import datetime
import pandas as pd
import ta
import trading_strategies.visualise as v


class MacdRsiSma:

    # loading the data in from file_path
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.close = self.df['close']

    # calculates the 5 period sma
    def calculate_5sma(self):
        self.df['5sma'] = self.df['close'].rolling(window=5).mean()

    # calculates the macd line
    def calculate_macd_line(self):
        self.df['macd_line'] = ta.trend.MACD(close=self.close).macd()

    # calculate the macd signal (a 9 period ema of the macd line)
    def calculate_macd_signal(self):
        self.df['macd_signal'] = ta.trend.MACD(close=self.close).macd_signal()

    # calculate the rsi
    def calculate_rsi(self):
        # initialise RSI indicator
        rsi_ind = ta.momentum.RSIIndicator(close = self.df['close'], window = 14)
        # generate RSI-2
        self.df['rsi'] = rsi_ind.rsi()

    def determine_signal(self, dframe):
        action = 0

        sma_5 = dframe['5sma']
        macd_line = dframe['macd_line']
        macd_signal = dframe['macd_signal']
        rsi = dframe['rsi']
        close = dframe['close']

        # buy if close price is higher than the moving average, rsi reads less than 30 and the macd line crosses up through macd signal line
        if (sma_5.iloc[-1] < close.iloc[-1]) and (macd_line.iloc[-2] < macd_signal.iloc[-2]) and \
                (macd_line.iloc[-1] > macd_signal.iloc[-1]) and (macd_line.iloc[-1] < 0 and rsi.iloc[-1] < 30):
            action = 1

        # sell if close price less than moving average, rsi reads over 70, and macd line crosses down through signal line
        elif (close.iloc[-1] < sma_5.iloc[-1]) and (macd_line.iloc[-1] > 0 and rsi.iloc[-1] > 70) and \
                (macd_line.iloc[-2] > macd_signal.iloc[-2]) and (macd_line.iloc[-1] < macd_signal.iloc[-1]):
            action = -1

        # return buy sell or hold and the difference between the 5 period moving average and the close
        return (action, sma_5.iloc[-1] - close.iloc[-1])

    # Runs the macd and psar indicators with 5sma
    def run_macd_rsi_sma(self):
        self.calculate_5sma()
        self.calculate_macd_line()
        self.calculate_macd_signal()
        self.calculate_rsi()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' 
    the following methods are for plotting
    '''
    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 36

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end-1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-36:])[0]
        plot_df.loc[plot_df.index[-1], 'signal'] = action

    def plot_graph(self):
        # make a copy so original is unimpacted
        plot_df = self.df.copy(deep=False)

        self.find_all_signals(plot_df)

        plot_df['0_line'] = 0
        plot_df['30_line'] = 30
        plot_df['70_line'] = 70

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(self.df['rsi'], panel=1, color='b', width=1, ylabel='rsi')
        visualisation.add_subplot(plot_df['30_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')
        visualisation.add_subplot(plot_df['70_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')
        visualisation.add_subplot(plot_df['5sma'], color='b', width=0.75)
        visualisation.add_subplot(plot_df['macd_line'], panel=2, color='r', width=1, ylabel='macd line (red)')
        visualisation.add_subplot(self.df['macd_signal'], panel=2, color='b', width=1, ylabel='macd signal (blue)')
        visualisation.add_subplot(plot_df['0_line'], panel=2, color='k', secondary_y=False, width=0.75, linestyle='solid')

        # create final plot with title
        visualisation.plot_graph("MACD with RSI and SMA strategy")



