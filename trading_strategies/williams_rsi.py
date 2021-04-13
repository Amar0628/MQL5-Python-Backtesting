# -*- coding: utf-8 -*-
"""

@author: caitlin

This strategy uses the Williams%R indicator. This momentum indicator oscillates between 0 and -100, and shows
how the current price compares to a 14 day look back period, where a reading near -100 indicates the market is
near the lowest low and a reading near 0 indicates the market is near the highest high. This strategy combines
an 8 period rsi.
"""


import pandas as pd
import trading_strategies.visualise as v
import ta


class WilliamsRsi:

    # loading the data in from file_path
    def __init__(self, file_path):
        # self.max_window = 150  #uncomment for graphing purposes
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    # Calculate the williams indicator
    def calculate_williams_indicator(self):
        will_ind = ta.momentum.WilliamsRIndicator(high = self.high, low = self.low, close = self.close)
        self.df['williams_indicator'] = will_ind.wr()


    def calculate_rsi(self):
        rsi_ind = ta.momentum.RSIIndicator(self.df['close'], window = 8)
        self.df['rsi'] = rsi_ind.rsi()


    def determine_signal(self, dframe):
        dframe['signal'] = 0

        # BUY signal: when williams indicator is less than -70 and rsi is less than 30 within the last 3 candles
        dframe.loc[(((dframe['williams_indicator'].shift(2) < -70) | (dframe['williams_indicator'].shift(1) < -70) | (dframe['williams_indicator'] < -70) | (dframe['williams_indicator'].shift(3) < -70))
                     & ((dframe['rsi'] < 30) | (dframe['rsi'].shift(1) < 30) | (dframe['rsi'].shift(2) < 30))), 'signal'] = 1

        # SELL signal: when williams indicator is greater than -30 and rsi is greater than 70 within last 3 candles
        dframe.loc[(((dframe['williams_indicator'].shift(2) > -30) | (dframe['williams_indicator'].shift(1) > -30) | (dframe['williams_indicator'] > -30) | (dframe['williams_indicator'].shift(3) > -30))
                     & ((dframe['rsi'] > 70) | (dframe['rsi'].shift(1) > 70) | (dframe['rsi'].shift(2) > 70))), 'signal'] = -1

        # return buy sell or hold signal and the value of the williams indicator
        signal_col = dframe.columns.get_loc('signal')
        return (dframe.iloc[-1, signal_col], dframe['williams_indicator'].iloc[-1])

    # Runs the indicator
    def run_williams_indicator(self):
        self.calculate_williams_indicator()

        self.calculate_rsi()

        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 100  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

            # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-100:])[0]

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

        # add subplots of williams indicator and rsi
        visualisation.add_subplot(plot_df['williams_indicator'], panel=1, color="blue")
        visualisation.add_subplot(line_70, panel=1, color="green")
        visualisation.add_subplot(line_30, panel=1, color="black")
        visualisation.add_subplot(plot_df['rsi'], panel=2)
        visualisation.add_subplot(line_70, panel=2, color="green")
        visualisation.add_subplot(line_30, panel=2, color="black")


        # create final plot with title
        visualisation.plot_graph("Williams Rsi Trading Strategy")


