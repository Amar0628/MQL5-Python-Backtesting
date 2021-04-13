import pandas as pd
import ta
import trading_strategies.visualise as v
import numpy as np

'''
@author: Caitlin


This strategy combines Keltner Channels with ADX. Buy signals are given when at least 3 candles
are at or below the low band, and oversold conditions are confirmed by an adx reading of at least 25.
Sell signals are given when at least 3 candles are at or above the high band, and overbought conditions are
confirmed by an adx reading of at least 20.
'''


class KeltnerAdx:

    def __init__(self, file_path):
        #self.max_window = 150 #uncomment for graphing purposes
        self.df = pd.read_csv(file_path)
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    def calculate_band_upper(self):
        band_up_ind = ta.volatility.KeltnerChannel(high=self.high, low=self.low, close=self.close, n=20)
        self.df['k_band_upper'] = band_up_ind.keltner_channel_hband()

    def calculate_band_lower(self):
        band_low_ind = ta.volatility.KeltnerChannel(high=self.high, low=self.low, close=self.close, n=20)
        self.df['k_band_lower'] = band_low_ind.keltner_channel_lband()

    def calculate_band_width(self):
        band_width = ta.volatility.KeltnerChannel(high = self.high, low = self.low, close = self.close, n=20)
        self.df['band_width'] = band_width.keltner_channel_wband()

    def calculate_adx(self):
        adx_ind = ta.trend.ADXIndicator(high=self.high, low=self.low, close=self.close, n=20)
        self.df['adx'] = adx_ind.adx()

    def determine_signal(self, dframe):

        # initialise all signals to hold: 0
        dframe['signal'] = 0

        # BUY SIGNAL: adx is >= 25 and at least 3 candles are less than or touch the lower keltner band
        dframe.loc[((dframe['high'] <= dframe['k_band_lower'])
                     & (dframe['high'].shift(1) <= dframe['k_band_lower'].shift(1))
                     & (dframe['high'].shift(2) <= dframe['k_band_lower'].shift(2)) & (dframe['adx'] >= 20)
                    ), 'signal'] = 1

        # SELL SIGNAL: adx is >=25 and at least 3 candles are greater than or touch the upper keltner band
        dframe.loc[((dframe['low'] >= dframe['k_band_upper'])
                     & (dframe['low'].shift(1) >= dframe['k_band_upper'].shift(1))
                     & (dframe['low'].shift(2) >= dframe['k_band_upper'].shift(2)) & (dframe['adx'] >= 20)
                     ), 'signal'] = -1

        # return final data point's signal and bandwidth
        signal_col = dframe.columns.get_loc('signal')
        return (dframe.iloc[-1, signal_col], dframe['band_width'].iloc[-1])

    def run_keltner_adx(self):

        self.calculate_band_lower()
        self.calculate_band_upper()
        self.calculate_adx()
        self.calculate_band_width()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 150  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

            # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-150:])[0]

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

        line_20 = [20] * self.max_window

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(line_20, panel=1, color="orange")
        visualisation.add_subplot(plot_df['adx'], panel=1, ylabel="Adx")
        visualisation.add_subplot(plot_df['k_band_upper'], color="blue")
        visualisation.add_subplot(plot_df['k_band_lower'], color="pink")

        # create final plot with title
        visualisation.plot_graph("Keltner Adx Trading Strategy")