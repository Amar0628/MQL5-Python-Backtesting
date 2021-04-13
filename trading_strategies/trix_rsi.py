import pandas as pd
import ta
import trading_strategies.visualise as v
import numpy as np

'''
author: Caitlin
This strategy uses the TRIX indicator and the RSI indicator to determine buy/sell signals.
TRIX is a triple smoothed Exponential Moving Average (EMA), eg the EMA of an EMA of an EMA.
The Relative Strength Index is a momentum indicator measuring speed and change of price movements.
'''


class TrixRsi:
    def __init__(self, file_path):
        #self.max_window = 200  # uncomment for graphing purposes
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    def calculate_trix_indicator(self):
        # initialise trix indicator
        trix_ind = ta.trend.TRIXIndicator(close = self.close, window=15)
        self.df['trix'] = trix_ind.trix()

    def calculate_signal_line(self):
        #a 9 period ema on trix
        self.df['signal_line'] = ta.utils.ema(self.df['trix'], 9)

    def calculate_rsi(self):
        # initialise rsi indicator
        rsi_ind = ta.momentum.RSIIndicator(close=self.close)
        self.df['rsi'] = rsi_ind.rsi()

    def determine_signal(self, dframe):

        # initialise all signals to hold: 0
        dframe['signal'] = 0

        # BUY SIGNAL: if TRIX is below -0.01 and RSI shows oversold within last 3 candles place buy order
        dframe.loc[(((dframe['trix'] < -0.01) | (dframe['trix'].shift(1) < -0.01) | (dframe['trix'].shift(2) < -0.01))
                    & ((dframe['rsi'] < 35) | (dframe['rsi'].shift(1) < 35) | (dframe['rsi'].shift(2) < 35))), 'signal'] = 1

        # SELL SIGNAL: if TRIX is above 0.01 and RSI shows overbought within last 3 candles place sell order
        dframe.loc[(((dframe['trix'] > 0.01) | (dframe['trix'].shift(1) > 0.01) | (dframe['trix'].shift(2) > 0.01))
                    & ((dframe['rsi'] > 65) | (dframe['rsi'].shift(1) > 65) | (dframe['rsi'].shift(2) > 65))), 'signal'] = -1

        # return final data point's signal and the value of the trix signal line
        signal_col = dframe.columns.get_loc('signal')
        return (dframe.iloc[-1, signal_col], dframe['signal_line'].iloc[-1])

    def run_trix_rsi(self):
        self.calculate_trix_indicator()
        self.calculate_signal_line()
        self.calculate_rsi()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 200  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

            # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-200:])[0]

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
        line_neg = [-0.01] * self.max_window
        line_pos = [0.01] * self.max_window

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(plot_df['trix'], panel=1, color="orange", ylabel="Trix Line")
        visualisation.add_subplot(plot_df['rsi'], panel=2, ylabel="Rsi")
        visualisation.add_subplot(line_30, panel=2)
        visualisation.add_subplot(line_70, panel=2)
        visualisation.add_subplot(line_neg, panel=1)
        visualisation.add_subplot(line_pos, panel=1)


        # create final plot with title
        visualisation.plot_graph("Trix Rsi Strategy")