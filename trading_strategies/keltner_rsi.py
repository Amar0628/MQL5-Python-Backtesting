import pandas as pd
import ta
import mplfinance as mpf
import numpy as np

'''
@author: Caitlin

This strategy uses the keltner channel and rsi2 indicator to determine when to place buy and sell orders
The combination with the rsi2 aims to filter out false signals, where the rsi2 shows whether conditions
are overbought or oversold, and candlesticks rising out of the top channel indicating a sell signal and 
dipping below the lower channel indicate a buy signal
'''

class KeltnerRsi:
    def __init__(self, file_path):
        #self.max_window = 50 # uncomment for graphing purposes
        self.df = pd.read_csv(file_path)
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    def calculate_band_upper(self):
        band_up_ind = ta.volatility.KeltnerChannel(high=self.high, low=self.low, close=self.close, n=20)
        self.df['k_band_upper'] = band_up_ind.keltner_channel_hband()

    def calculate_band_lower(self):
        band_low_ind = ta.volatility.KeltnerChannel(high=self.high, low=self.low, close=self.close, n=20)
        self.df['k_band_lower'] = band_low_ind.keltner_channel_lband()

    def calculate_rsi2(self):
        rsi2_ind = ta.momentum.RSIIndicator(close=self.close, n=2)
        self.df['rsi2'] = rsi2_ind.rsi()

    def determine_signal(self, dframe):

        # initialise all signals to hold: 0
        dframe['signal'] = 0

        # BUY SIGNAL: rsi2 displays oversold conditions ie less than 10 and at least 3 candlesticks are below the lower band
        dframe.loc[(((dframe['rsi2'] < 50) | (dframe['rsi2'].shift(1) < 50) | (dframe['rsi2'].shift(2) < 50) | (dframe['rsi2'].shift(3) < 50))
                     & ((dframe['close'] <= dframe['k_band_lower']) | (dframe['close'].shift(1) <= dframe['k_band_lower'].shift(1))
                        | (dframe['close'].shift(2) <= dframe['k_band_lower'].shift(2))| (dframe['close'].shift(3) <= dframe['k_band_lower'].shift(3)))), 'signal'] = 1

        # SELL SIGNAL: rsi2 displays overbought conditions ie greater than 90 and at least 3 candlesticks are above the upper band
        dframe.loc[(((dframe['rsi2'] > 50) | (dframe['rsi2'].shift(1) > 50) | (dframe['rsi2'].shift(2) > 50) | (dframe['rsi2'].shift(3) > 50))
                     & ((dframe['close'] >= dframe['k_band_upper']) | (dframe['close'].shift(1) >= dframe['k_band_upper'].shift(1))
                        | (dframe['close'].shift(2) >= dframe['k_band_upper'].shift(2)) | (dframe['close'].shift(3) >= dframe['k_band_upper'].shift(3)))), 'signal'] = -1

        # return final data point's signal and value of rsi2
        signal_col = dframe.columns.get_loc('signal')
        return(dframe.iloc[-1, signal_col], dframe['rsi2'].iloc[-1])

    def run_keltner_rsi2(self):

        self.calculate_band_lower()
        self.calculate_band_upper()
        self.calculate_rsi2()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 50  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

            # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-50:])[0]

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

        line_30 = [30] * self.max_window
        line_70 = [70] * self.max_window

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(plot_df['rsi2'], panel=1, color="orange")
        visualisation.add_subplot(line_30, panel=1, color="blue")
        visualisation.add_subplot(line_70, panel=1, color="green")
        visualisation.add_subplot(plot_df['k_band_upper'])
        visualisation.add_subplot(plot_df['k_band_lower'])

        # create final plot with title
        visualisation.plot_graph("Keltner RSI Trading Strategy")