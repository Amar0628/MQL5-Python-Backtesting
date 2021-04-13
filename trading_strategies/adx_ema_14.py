import pandas as pd
import ta
import numpy as np
import trading_strategies.visualise as v
'''
### Author:Vita ###
Strategy from:
https://forextester.com/blog/adx-14-ema-strategy
This strategy uses ADX and 14EMA for buy and sell signals
'''


class ADXEMA14:
    # constructor
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.close = self.df['close']
        self.high = self.df['high']
        self.low = self.df['low']

    def add_adx(self):
        self.df['adx'] = ta.trend.ADXIndicator(high=self.high, low=self.low, close=self.close).adx()
        self.df['adx'].replace(0.0, np.nan, inplace=True)

    def calculate_ema_14(self):
        self.df['14ema'] = self.df['close'].ewm(span=14, adjust=False).mean()


    def determine_signal(self, dframe):

        adx = dframe['adx']
        ema14 = dframe['14ema']
        open = dframe['open']
        close = dframe['close']

        action = 0

        # SELL CRITERIA: if candlestick is bearish, close is less than 14 EMA and ADX indicator has crossed above 25:
        if (open.iloc[-1] > close.iloc[-1]) and (close.iloc[-1] < ema14.iloc[-1]) and (adx.iloc[-2] < 25 and adx.iloc[-1] > 25):
            action = -1
        # BUY CRITERIA: if candlestick is bullish, close is greater than 14EMA and ADX indicator has crossed above 25
        elif (close.iloc[-1] > open.iloc[-1]) and (close.iloc[-1] > ema14.iloc[-1]) and (adx.iloc[-2] < 25 and adx.iloc[-1] > 25):
            action = 1

        return action, dframe['adx'].iloc[-1],

    def run_adx_ema_14(self):
        self.add_adx()
        self.calculate_ema_14()
        return self.determine_signal(self.df), self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 40

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-40:])[0]
        plot_df.loc[plot_df.index[-1], 'signal'] = action

    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)

        self.find_all_signals(plot_df)

        plot_df['25_line'] = 25

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(plot_df['adx'], panel=1, color='m', ylabel='adx')
        visualisation.add_subplot(plot_df['14ema'], color='violet', width=0.75)
        visualisation.add_subplot(plot_df['25_line'], panel=1, color='b', width=0.75, linestyle='solid')


        # create final plot with title
        visualisation.plot_graph("ADX 14-EMA Strategy")


