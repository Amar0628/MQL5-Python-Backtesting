# -*- coding: utf-8 -*-
"""

@author: caitlin
The strategy uses the aroon indicator to determine buy and sell signals.
The aroon up indicator shows how many periods since a 25 period high, and similarly the aroon down
indicator shows how many periods since a 25 period low. Readings range from 0 to 100. Generally the
market is bullish if aroon up > 50 and bearish if aroon down < 50. This is combined with the adx
to determine if there is a strong trend, the adx requires a reading of over 20.
"""

import pandas as pd
import trading_strategies.visualise as v
import ta


class AroonAdx:

    # loading the data in from file_path
    def __init__(self, file_path):
        self.max_window = 100
        self.df = self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    # Calculate the aroon up line
    def calculate_aroon(self):
        aroon_ind = ta.trend.AroonIndicator(close=self.close)
        self.df['aroon'] = aroon_ind.aroon_indicator()

    # Calculate the aroon up line
    def calculate_aroon_up(self):
        aroon_up = ta.trend.aroon_up(close=self.close)
        self.df['aroon_up'] = aroon_up

    # Calculate the aroon down line
    def calculate_aroon_down(self):
        aroon_down = ta.trend.aroon_down(close=self.close)
        self.df['aroon_down'] = aroon_down

    def calculate_adx(self):
        adx_ind = ta.trend.ADXIndicator(self.df['high'], self.df['low'], self.df['close'], window=20)
        self.df['adx'] = adx_ind.adx()


    def determine_signal(self, dframe):
        dframe['signal'] = 0

        # A buy entry signal is given when aroon up > 50 and aroon down < 50 and adx > 20
        dframe.loc[((((dframe['aroon_up'] > 50) & (dframe['aroon_down'] < 50)) | ((dframe['aroon_up'].shift(1) > 50) & (dframe['aroon_down'].shift(1) < 50))
                      | ((dframe['aroon_up'].shift(2) > 50) & (dframe['aroon_down'].shift(2) < 50)) | ((dframe['aroon_up'].shift(3) > 50) & (dframe['aroon_down'].shift(3) < 50))
                      | ((dframe['aroon_up'].shift(4) > 50) & (dframe['aroon_down'].shift(4) < 50)))
                     & (dframe['adx'] > 20)), 'signal'] = 1

        # A sell entry signal is given when aroon down > 50 and aroon up < 50 and adx > 20
        dframe.loc[((((dframe['aroon_down'] > 50) & (dframe['aroon_up'] < 50)) | ((dframe['aroon_down'].shift(1) > 50) & (dframe['aroon_up'].shift(1) < 50))
                       | ((dframe['aroon_down'].shift(2) > 50) & (dframe['aroon_up'].shift(2) < 50)) | ((dframe['aroon_down'].shift(3) > 50) & (dframe['aroon_up'].shift(3) < 50))
                       | ((dframe['aroon_down'].shift(4) > 50) & (dframe['aroon_up'].shift(4) < 50)))
                      & (dframe['adx'] > 20)), 'signal'] = -1

        signal_col = dframe.columns.get_loc('signal')
        return (dframe.iloc[-1, signal_col], dframe['aroon'].iloc[-1])

    # Runs the indicator
    def run_aroon_adx(self):
        self.calculate_aroon()
        self.calculate_aroon_up()
        self.calculate_aroon_down()
        self.calculate_adx()
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

        line_50 = [50] * self.max_window
        line_20 = [20] * self.max_window

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(plot_df['adx'], panel=2, color="orange")
        visualisation.add_subplot(line_20, panel=2, color="blue")
        visualisation.add_subplot(plot_df['aroon_up'], panel=1, ylabel="Aroon Up")
        visualisation.add_subplot(plot_df['aroon_down'], panel=1, ylabel="Aroon Down")
        visualisation.add_subplot(line_50, panel=2, color="black")

        # create final plot with title
        visualisation.plot_graph("Aroon Adx Trading Strategy")