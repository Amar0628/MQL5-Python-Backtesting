import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:
https://www.ig.com/au/trading-strategies/best-forex-trading-strategies-and-tips-190520#Bladerunner

The first candlestick that touches the EMA is called the ‘signal candle’,
The second candle that moves away from the EMA again is the ‘confirmatory candle’.
Traders would place their open orders at this price level to take advantage of the rebounding price.

'''

class BladeRunner:

    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        #self.df = pd.DataFrame(file_path)

    def add_ema(self):
        self.df['ema_20'] = self.df['close'].ewm(span = 20, min_periods = 20).mean()

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0
        # BUY if first candle stick touches ema and then next candle stick rebounds off it
        if((dframe['low'].iloc[-2] <= dframe['ema_20'].iloc[-2] and dframe['ema_20'].iloc[-2] <= dframe['high'].iloc[-2]) & (dframe['close'].iloc[-1] > dframe['close'].iloc[-2])):
            signal = 1

        # SELL if first candle stick touches ema and then next candle stick rebounds off it
        if((dframe['low'].iloc[-2] <= dframe['ema_20'].iloc[-2] and dframe['ema_20'].iloc[-2] <= dframe['high'].iloc[-2]) & (dframe['close'].iloc[-1] < dframe['close'].iloc[-2])):
            signal = -1

        return signal

    # determine and return additional useful information for last data point in given df
    def determine_additional_info(self, dframe):

        # strength of rebound
        return dframe.iloc[-1]['close'] - dframe.iloc[-2]['close']

    # run strategy
    def run_blade_runner(self):

        #perform calculations
        self.add_ema()

        #generate data for return tuple at index -1 in the dataset aka most recent data point
        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        #create return tuple and append data
        result = []
        result.append(signal)
        result.append(additional_info)

        return tuple(result), self.df

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 200 # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-200:])

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

        # add subplots of 20 period ema
        visualisation.add_subplot(plot_df['ema_20'], color="orange")
        #visualisation.add_subplot(plot_df['awesome_oscillato'], type="bar", panel = 1, ylabel="Blade\nRunner")

        # create final plot with title
        visualisation.plot_graph("Blade Runner Strategy")

#strategy = BladeRunner(r"C:\Users\Wilson\Documents\INFO3600\AUD_USD_H4.csv")
#print(strategy.run_blade_runner())
#strategy.plot_graph()
