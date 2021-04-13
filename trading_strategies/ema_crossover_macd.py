# -*- coding: utf-8 -*-
"""
@author: vita
This strategy uses the crossover between 9EMA and 21EMA with MACD histogram as confirmation to avoid false signals
http://www.forexfunction.com/trading-strategy-of-ema-crossover-with-macd
"""
import pandas as pd
import ta
import trading_strategies.visualise as v

class EMACrossoverMACD:

    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))

    def calculate_21_ema(self):
        self.df['21ema'] = self.df['close'].ewm(span=21, adjust=False).mean()

    def calculate_9_ema(self):
        self.df['9ema'] = self.df['close'].ewm(span=9, adjust=False).mean()

    def add_macd_diff(self):
        self.df['macd_histogram'] = ta.trend.MACD(close = self.df['close']).macd_diff()

    def determine_signal(self, dframe):
        ema9 = dframe['9ema']
        ema21 = dframe['21ema']
        histogram = dframe['macd_histogram']
        close = dframe['close']

        action = 0

        # SELL CRITERIA: 9EMA crosses below 21EMA followed by a MACD histogram crossover into negatives
        if (ema9.iloc[-2] < ema21.iloc[-2] and ema9.iloc[-3]>ema21.iloc[-3]) and ((histogram.iloc[-1] < 0 and histogram.iloc[-2] > 0) or (histogram.iloc[-1] > 0 and histogram.iloc[-2] < 0)):
            action = -1

        # BUY CRITERIA: 9EMA crosses above 21EMA followed by a MACD histogram crossover ito positives
        if (ema9.iloc[-2] > ema21.iloc[-2] and ema9.iloc[-3]<ema21.iloc[-3]) and ((histogram.iloc[-1] > 0 and histogram.iloc[-2] < 0) or (histogram.iloc[-1] < 0 and histogram.iloc[-2] > 0)):
            action = 1

        return action, ema21.iloc[-1]-close.iloc[-1],

    def run_ema_crossover_macd(self):
        self.calculate_21_ema()
        self.calculate_9_ema()
        self.add_macd_diff()
        return self.determine_signal(self.df), self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 36

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-36:])[0]
        plot_df.loc[plot_df.index[-1], 'signal'] = action

    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)
        self.find_all_signals(plot_df)

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(plot_df['macd_histogram'], panel=1, color='b', type='bar')
        visualisation.add_subplot(plot_df['9ema'], panel=0, color='pink', width=0.75)
        visualisation.add_subplot(plot_df['21ema'], panel=0, color='turquoise', width=0.75)

        # create final plot with title
        visualisation.plot_graph("EMA Crossover with MACD Strategy")




