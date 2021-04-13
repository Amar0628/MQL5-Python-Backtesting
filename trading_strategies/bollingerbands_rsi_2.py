import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:

https://www.theancientbabylonians.com/the-bollinger-bands-and-relative-strength-index-rsi-strategy/

This strategy identifies over bought and over sold conditions and back checks this against the bollinger band
to ensure robustness of signals.

'''

class BollingerBandsAndRSI2:

    #constructor
    def __init__(self, file_path):
        #self.df = pd.DataFrame(file_path)
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))

    # add bollinger bands (bb) to indicate volatilty
    def add_bollinger_bands(self):
        self.df['bb_high_band'] = ta.volatility.bollinger_hband(self.df['close'], window = 14, window_dev= 2, fillna = False)
        self.df['bb_low_band'] = ta.volatility.bollinger_lband(self.df['close'], window = 14, window_dev = 2, fillna = False)

    # add rsi to identify overbought/oversold conditions
    def add_rsi(self):
        self.df['rsi'] = ta.momentum.rsi(self.df['close'], window = 14, fillna = False)

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0

        #BUY if price is below low bollinger band and rsi is less than 30
        if((dframe['close'].iloc[-1] <= dframe['bb_low_band'].iloc[-1]) & (dframe['rsi'].iloc[-1] <= 30)):
            signal = 1

        #SELL if price is above high bollinger band as rsi is greater than 70
        if((dframe['close'].iloc[-1] >= dframe['bb_high_band'].iloc[-1]) & (dframe['rsi'].iloc[-1] >= 70)):
            signal = -1

        return signal

    # determine and return additional useful information
    def determine_additional_info(self, dframe):

        return dframe.iloc[-1]['bb_high_band'] - dframe.iloc[-1]['bb_low_band']

    # run the strategy
    def run_bollingerbands_rsi_2(self):

        # perform calculations
        self.add_bollinger_bands()
        self.add_rsi()

        # generate data for return tuple
        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        #create return tuple and append data
        result = []
        result.append(signal)
        result.append(additional_info)

        return tuple(result), self.df

    ''' The following methods are for plotting '''

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

        # add subplots of bb and rsi
        visualisation.add_subplot(plot_df['bb_high_band'], color="orange")
        visualisation.add_subplot(plot_df['bb_low_band'], color="orange")
        visualisation.add_subplot(plot_df['rsi'], type="line", panel = 1, ylabel="RSI")

        # create final plot with title
        visualisation.plot_graph("Bollinger Bands RSI 2 Strategy")

#strategy = BollingerBandsAndRSI2(r"C:\Users\Wilson\Documents\INFO3600\info3600_group1-project\back_testing\3yr_historical_data\3YR_AUD_USD\FXCM_AUD_USD_H4.csv")
#strategy.run_bollingerbands_rsi_2()
#strategy.plot_graph()
