# -*- coding: utf-8 -*-
"""
@author: caitlin
This strategy uses Donchian Channels. It examines whether the close is higher or lower than the middle donchian line.
"""

import pandas as pd
import trading_strategies.visualise as v
import ta

class DonchianMiddle:
    # loading the data in from file_path
    def __init__(self, file_path):
        self.max_window = 1001  # uncomment for graphing purposes
        self.df = pd.read_csv(file_path)[-self.max_window:]
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']


    def calculate_donchian_middle(self):
        donch_mid_ind = ta.volatility.DonchianChannel(high=self.high, low=self.low, close=self.close, n=20)
        self.df['donch_mid'] = donch_mid_ind.donchian_channel_mband()


    def determine_signal(self, dframe):
        dframe['signal'] = 0
        # A buy entry signal is given when close exceeds the middle donchian line
        dframe.loc[(dframe['close'] > dframe['donch_mid']), 'signal'] = 1

        # A sell entry signal is given when close goes below the middle donchian line
        dframe.loc[(dframe['close'] < dframe['donch_mid']), 'signal'] = -1


        signal_col = dframe.columns.get_loc('signal')
        return (dframe.iloc[-1, signal_col], dframe['donch_mid'].iloc[-1])

    # Runs the indicator
    def run_donchian_middle(self):
        self.calculate_donchian_middle()
        signal = self.determine_signal(self.df)
        return signal, self.df

    '''
        the following methods are for plotting
    '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
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

        # add subplot of donchian middle band
        visualisation.add_subplot(plot_df['donch_mid'], color="blue", ylabel="Donchian\nMiddle Band")

        # create final plot with title
        visualisation.plot_graph("Donchian Middle Band Trading Strategy")
