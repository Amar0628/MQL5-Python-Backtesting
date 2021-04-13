import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:
https://www.tradingwithrayner.com/donchian-channel-indicator/#atr
'''

class DonchianATR():

    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        #self.df = pd.DataFrame(file_path)
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    def add_atr(self):
        self.df['atr'] = ta.volatility.AverageTrueRange(high = self.high, low = self.low, close = self.close, n = 14).average_true_range()

    def add_atr_two_year_low(self):
        self.df['atr_two_year_low'] = self.df['atr'].shift(1).rolling(window = 48).min()

    def add_donchian_high_band(self):
        self.df['donchian_high_band'] = ta.volatility.DonchianChannel(high = self.high, low = self.low, close = self.close, n = 20).donchian_channel_hband()

    def add_donchian_low_band(self):
        self.df['donchian_low_band'] = ta.volatility.DonchianChannel(high = self.high, low = self.low, close = self.close, n = 20).donchian_channel_lband()

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0

        # BUY if ATR is below 2 year low and price breaks above donchian high band
        if((dframe['atr'].iloc[-1] < dframe['atr_two_year_low'].iloc[-1]) & (dframe['high'].iloc[-1] >= dframe['donchian_high_band'].iloc[-1])):
            signal = 1

        # SELL if ATR is below 2 year low and price drops below donchian low band
        if((dframe['atr'].iloc[-1] < dframe['atr_two_year_low'].iloc[-1]) & (dframe['low'].iloc[-1] <= dframe['donchian_low_band'].iloc[-1])):
            signal = -1

        return signal

    # determine and return additional useful information
    def determine_additional_info(self, dframe):

        return dframe.iloc[-1]['donchian_high_band'] - dframe.iloc[-1]['atr_two_year_low']

    def run_donchian_atr(self):

        # perform calculations
        self.add_atr()
        self.add_atr_two_year_low()
        self.add_donchian_high_band()
        self.add_donchian_low_band()

        # generate data for return tuple
        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        # create return tuple and append data
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

        # add subplots of donchian channels
        visualisation.add_subplot(plot_df['donchian_high_band'], color="orange")
        visualisation.add_subplot(plot_df['donchian_low_band'], color="orange")

        visualisation.add_subplot(plot_df['atr'], type="line", panel = 1, ylabel="ATR and 2 year low")
        visualisation.add_subplot(plot_df['atr_two_year_low'], type="line", panel = 1)

        # create final plot with title
        visualisation.plot_graph("Donchian ATR Strategy")
