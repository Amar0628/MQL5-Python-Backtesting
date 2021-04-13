import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import ta
import trading_strategies.visualise as v

'''
### Author: Wilson ###
Strategy from:
https://medium.com/swlh/creating-a-trading-strategy-using-the-rsi-the-bollinger-bands-new-ideas-using-python-4115e1fdfbba

This strategy identifies over bought and over sold conditions and back checks this against the bollinger band
spreads to ensure robustness of signals.

Personal modifications:
    - I have added an extra buy criteria when bb spread is large to take advantage of uptrending markets
    - I have added an extra sell criteria to sell when bb spread is large to take advantage of down trending markets
    - I have lowered widening variable to 1.9x standard dev (as opposed to 2) to increase sensitivity to prices
    - I have added bollinger bands to buy/sell criteria to increase quality signals
    - I have increased the rsi oversold threshold to 0.6 to allow more buy signals

'''

class BollingerBandsAndRSI:

    # constructor
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        #self.df = pd.DataFrame(file_path)
        #self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume"))

        self.buy_found = False
        self.sell_found = False

    # add bollinger bands (bb) to indicate volatilty
    def add_bollinger_bands(self):
        self.df['bb_high_band'] = ta.volatility.bollinger_hband(self.df['close'], n = 14, ndev = 2, fillna = False)
        self.df['bb_low_band'] = ta.volatility.bollinger_lband(self.df['close'], n = 14, ndev = 2, fillna = False)

    # add bollinger spreads to indicate the volatility of the bb
    def add_bollinger_spread(self):
        self.df['bb_spread'] = self.df['bb_high_band'] - self.df['bb_low_band']

    # add bollinger spread standard deviations to indicate bb spread volatility
    def add_bollinger_spread_standard_deviation(self):
        self.df['bb_spread_stdev'] = self.df['bb_spread'].rolling(window = 14).std()

    # add bollinger spread moving average to find middle bb spread line
    def add_bollinger_spread_moving_average(self):
        self.df['bb_spread_ma'] = self.df['bb_spread'].rolling(window = 14).mean()

    # add bollinger spread bands to create "widening variable"
    def add_bollinger_spread_bands(self):
        self.df['bb_spread_high_band'] = self.df['bb_spread_ma'] + 1.90*self.df['bb_spread_stdev']
        self.df['bb_spread_low_band'] = self.df['bb_spread_ma'] - 1.90*self.df['bb_spread_stdev']

    # add rsi to identify overbought/oversold conditions
    def add_rsi(self):
        self.df['rsi'] = ta.momentum.rsi(self.df['close'], n = 14, fillna = False)

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0
        #print(dframe)
        # BUY if bb spread is within bands and RSI <= 30
        if((dframe['bb_spread'].iloc[-1] > dframe['bb_spread_low_band'].iloc[-1]) & (dframe['bb_spread'].iloc[-1] < dframe['bb_spread_high_band'].iloc[-1]) & (dframe['rsi'].iloc[-1] <= 50)):
            signal = 1
        # BUY if price breaks bb upper
        if(dframe['close'].iloc[-1] < dframe['bb_low_band'].iloc[-1]):
            signal = 1
        # BUY if BB spread is large and RSI >= 70
        if((dframe['bb_spread'].iloc[-1] >= dframe['bb_spread_high_band'].iloc[-1]) & (dframe['rsi'].iloc[-1] >= 70)):
            signal = 1

        # SELL if bb spread is within bands and RSI >= 70
        if((dframe['bb_spread'].iloc[-1] > dframe['bb_spread_low_band'].iloc[-1]) & (dframe['bb_spread'].iloc[-1] < dframe['bb_spread_high_band'].iloc[-1]) & (dframe['rsi'].iloc[-1] >= 70)):
            signal = -1
        # SELL if spread is large and RSI  <= 30
        if((dframe['bb_spread'].iloc[-1] >= dframe['bb_spread_high_band'].iloc[-1]) & (dframe['rsi'].iloc[-1] <= 50)):
            signal = -1
        # SELL if price breaks bb lower
        if(dframe['close'].iloc[-1] > dframe['bb_high_band'].iloc[-1]):
            signal = -1

        return signal

    # determine and return additional useful information
    def determine_additional_info(self, dframe):

        return dframe.iloc[-1]['bb_spread_high_band'] - dframe.iloc[-1]['bb_spread_low_band']

    # run strategy
    def run_bollingerbands_rsi(self):

        # perform calculations
        self.add_bollinger_bands()
        self.add_bollinger_spread()
        self.add_bollinger_spread_standard_deviation()
        self.add_bollinger_spread_moving_average()
        self.add_bollinger_spread_bands()
        self.add_rsi()

        # generate data for return tuple
        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        # create return tuple and append data
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
        visualisation.plot_graph("Bollinger Bands RSI Strategy")

#strategy = BollingerBandsAndRSI(r"C:\Users\Wilson\Documents\INFO3600\info3600_group1-project\back_testing\3yr_historical_data\3YR_AUD_USD\FXCM_AUD_USD_H4.csv")
#strategy.run_bollingerbands_rsi()
#strategy.plot_graph()
