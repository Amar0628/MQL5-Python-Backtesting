# https://www.incrediblecharts.com/indicators/mass_index.php

import pandas as pd
import ta
import trading_strategies.visualise as v

class EMAMI:
    def __init__(self, file_path):
        #self.df = pd.DataFrame(file_path)
        self.df = pd.read_csv(file_path)
        self.high = self.df['high']
        self.low = self.df['low']
        self.close = self.df['close']

    # calculates the EMA (ema) indicator using ta library, period of 9
    def calculate_ema(self):
        self.df['ema'] = self.df['close'].ewm(span=9, adjust=False).mean()

    # calculates the mass index (mi) using ta library
    def calculate_mi(self):
        self.df['mi'] = ta.trend.MassIndex(high = self.high, low = self.low).mass_index()  # n is left at the default of 9 and n2 is left at the default of 25

    def determine_signal(self, dframe):
        # initialise all signals to hold: 0
        signal = 0

        # BUY SIGNAL: when mi drops below 26.5 and ema is negatively sloped
        if dframe['mi'].iloc[-1] < 26.5 and dframe['mi'].iloc[-2] >= 26.5 and dframe['ema'].iloc[-1] < dframe['ema'].iloc[-2]:
            signal = 1
        # SELL SIGNAL: when mi drops below 26.5 and ema is positively sloped
        elif dframe['mi'].iloc[-1] < 26.5 and dframe['mi'].iloc[-2] >= 26.5 and dframe['ema'].iloc[-1] > dframe['ema'].iloc[-2]:
            signal = -1

        return (signal, dframe['ema'].iloc[-1])

    def run(self):
        self.calculate_ema()
        self.calculate_mi()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 42  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            additional_info = self.determine_signal(curr_window)[1]
            plot_df.loc[plot_df.index[end - 1], 'additional_info'] = additional_info
            end += 1
            start += 1

        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-42:])[0]

    def plot_graph(self):

        # deep copy of data so original is not impacted
        plot_df = self.df.copy(deep=True)

        # determine all signals for the dataset
        self.find_all_signals(plot_df)

        plot_df['zero_line'] = 0
        plot_df['mi_cross_line'] = 26.5

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of senkou span A and B to form the ichimoku cloud, and the parabolic sar dots
        visualisation.add_subplot(plot_df['ema'], color='orange', width=0.75)
        visualisation.add_subplot(plot_df['mi'], panel=1, color='m', width=0.75, ylabel='MI')
        visualisation.add_subplot(plot_df['mi_cross_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')

        # create final plot with title
        visualisation.plot_graph("EMA MI Strategy")
