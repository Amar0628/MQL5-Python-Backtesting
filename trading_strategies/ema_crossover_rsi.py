# -*- coding: utf-8 -*-
"""
@author: vita
This strategy uses the crossover between 6EMA and 12EMA with RSI
http://www.forexfunction.com/ema-crossover-and-rsi-simple-trading-strategy
"""
import datetime
import pandas as pd
import trading_strategies.visualise as v
import ta



class EMACrossoverRSI:

    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.close = self.df['close']

    def calculate_12_ema(self):
        self.df['12ema'] = self.df['close'].ewm(span=12, adjust=False).mean()

    def calculate_6_ema(self):
        self.df['6ema'] = self.df['close'].ewm(span=6, adjust=False).mean()

    def add_rsi(self):
        rsi_ind = ta.momentum.RSIIndicator(close=self.close, window=14)
        self.df['rsi'] = rsi_ind.rsi()

    def determine_signal(self, dframe):
        ema6 = dframe['6ema']
        ema12 = dframe['12ema']
        rsi = dframe['rsi']
        close = dframe['close']

        action = 0

        # SELL CRITERIA: when 6EMA crosses above 12EMA and RSI value has crossed below 50
        if (ema6.iloc[-1] < ema12.iloc[-1] and ema6.iloc[-2] > ema12.iloc[-2]) and (

                rsi.iloc[-1] < 50 and rsi.iloc[-2] > 50):
            action = -1

        # BUY CRITERIA: when 6EMA crosses below 12EMA and RSI value has crossed above 50
        if (ema6.iloc[-1] > ema12.iloc[-1] and ema6.iloc[-2] < ema12.iloc[-2]) and (
                rsi.iloc[-1] > 50 and rsi.iloc[-2] < 50):
            action = 1

        return (action, ema12.iloc[-1] - close.iloc[-1],)

    def run_ema_crossover_rsi(self):
        self.calculate_12_ema()
        self.calculate_6_ema()
        self.add_rsi()
        return self.determine_signal(self.df), self.df

    ''' The following methods are for plotting '''
    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 15

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-15:])[0]
        plot_df.loc[plot_df.index[-1], 'signal'] = action

    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)

        self.find_all_signals(plot_df)

        # preparing values for horizontal line at rsi values 80 and 20 for visual purposes
        plot_df['50_line'] = 50

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of RSI, 80 line and 20 line
        visualisation.add_subplot(plot_df['6ema'], panel=0, color='pink', width=0.75)
        visualisation.add_subplot(plot_df['12ema'], panel=0, color='b', width=0.75)
        visualisation.add_subplot(plot_df['rsi'], panel=1, color='m', width=0.75, ylabel='RSI')
        visualisation.add_subplot(plot_df['50_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')

        # create final plot with title
        visualisation.plot_graph("EMA Crossover with RSI strategy")


# # strategy = EMACrossoverRSI('/Users/vhuang/INFO3600/USD_JPY_M15.csv')
# # strategy = ThreeCrowSoldiersCandlesticksRsi('/Users/vhuang/INFO3600/FXCM_EUR_USD_H4_1.csv')
# strategy = EMACrossoverRSI('/Users/vhuang/INFO3600/FXCM_EUR_USD_H4.csv')
# signal = strategy.run_ema_crossover_rsi()
# print(signal)
# print(strategy.plot_graph())
