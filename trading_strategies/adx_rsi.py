import pandas as pd
import ta
import trading_strategies.visualise as v
import numpy as np

'''
This strategy uses the ADX indicator and RSI indicator to determine buy and sell signals.
The Average Directional Movement Index (ADX) measures the strength of trends, while the
Relative Strength Index is a momentum indicator measuring speed and change of price movements.
The market can be considered oversold if RSI measures below 30 and overbought if it measures
above 70. An ADX reading of over 20 indicates a strong trend while lower readings indicate a
lack of trend.

'''

class AdxRsi:
    def __init__(self, file_path):
        #self.max_window = 100 #uncomment for graphing purposes
        self.df = pd.read_csv(file_path)


    def calculate_adx(self):
        adx_ind = ta.trend.ADXIndicator(self.df['high'], self.df['low'], self.df['close'], n = 20)
        self.df['adx'] = adx_ind.adx()

    def calculate_rsi(self):
        rsi_ind = ta.momentum.RSIIndicator(self.df['close'], n = 2)
        self.df['rsi'] = rsi_ind.rsi()

    def determine_signal(self, dframe):

        # initialise all signals to hold: 0
        dframe['signal'] = 0

        # BUY SIGNAL: adx is above 20 and rsi reads below 30 implying oversold conditions
        dframe.loc[((dframe['adx'] > 20) & ((dframe['rsi'] <= 30) | (dframe['rsi'].shift(1) <= 30) | (dframe['rsi'].shift(2) <= 30) | (dframe['rsi'].shift(3) <= 30) | (dframe['rsi'].shift(4) <= 30))), 'signal'] = 1

        # SELL SIGNAL: adx is below 25 and rsi is showing overbought conditions, eg over 70
        dframe.loc[((dframe['adx'] > 20) & ((dframe['rsi'] >= 70) | (dframe['rsi'].shift(1) >= 70) | (dframe['rsi'].shift(2) >= 70) | (dframe['rsi'].shift(3) >= 70) | (dframe['rsi'].shift(4) >= 70))), 'signal'] = -1

        # return final data point's signal
        signal_col = dframe.columns.get_loc('signal')
        return(dframe.iloc[-1, signal_col], dframe['adx'].iloc[-1])

    def run_adx_rsi(self):
        self.calculate_rsi()
        self.calculate_adx()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

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

        line_30 = [30] * self.max_window
        line_70 = [70] * self.max_window
        line_20 = [20] * self.max_window

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(line_20, panel=1, color="orange")
        visualisation.add_subplot(plot_df['adx'], panel=1, ylabel="Adx")
        visualisation.add_subplot(plot_df['rsi'], panel=2, ylabel="Rsi")
        visualisation.add_subplot(line_30, panel=2, color="pink")
        visualisation.add_subplot(line_70, panel=2, color="blue")

        # create final plot with title
        visualisation.plot_graph("Adx Rsi Trading Strategy")