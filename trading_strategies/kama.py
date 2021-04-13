import pandas as pd
import ta
import trading_strategies.visualise as v
'''
### Author: Wilson ###
Strategy from:
https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/kaufmans-adaptive-moving-average-kama/

This strategy uses the KAMA indicator to analyze the behaviour of the market and predict future price movement

'''

class KAMA:

    def __init__(self, file_path):
        #self.df = pd.DataFrame(file_path)
        self.df = pd.read_csv(file_path)

    def add_kama(self):
        self.df['kama'] = ta.momentum.KAMAIndicator(close = self.df['close'], n = 10, pow1 = 2, pow2 = 30).kama()

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0

        # BUY if price crosses above KAMA
        if((dframe['close'].iloc[-2] < dframe['kama'].iloc[-2]) & (dframe['close'].iloc[-1] > dframe['kama'].iloc[-1])):
            signal = 1

        #SELL if price crosses below KAMA
        if((dframe['close'].iloc[-2] > dframe['kama'].iloc[-2]) & (dframe['close'].iloc[-1] < dframe['kama'].iloc[-1])):
            signal = -1

        return signal

    # determine and return additional useful information (kama value at signal point)
    def determine_additional_info(self, dframe):

        return dframe.iloc[-1]['kama']


    def run_kama(self):

        self.add_kama()

        signal = self.determine_signal(self.df)
        additional_info = self.determine_additional_info(self.df)

        result = []
        result.append(signal)
        result.append(additional_info)

        return tuple(result), self.df

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

        # add subplots of KAMA
        visualisation.add_subplot(plot_df['kama'], color="orange")

        # create final plot with title
        visualisation.plot_graph("KAMA Strategy")
