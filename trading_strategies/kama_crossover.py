import pandas as pd
import ta
import trading_strategies.visualise as v

# Source: https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/kaufmans-adaptive-moving-average-kama/



class KAMACrossover:

    def __init__(self, file_path):
        #self.df = pd.DataFrame(file_path)
        self.df = pd.read_csv(file_path)

    def add_kama_fast(self):
        self.df['kama_fast'] = ta.momentum.KAMAIndicator(close = self.df['close'], n = 10, pow1 = 2, pow2 = 30).kama()

    def add_kama_slow(self):
        self.df['kama_slow'] = ta.momentum.KAMAIndicator(close = self.df['close'], n = 10, pow1 = 5, pow2 = 30).kama()

    # determine and signal for particular index
    def determine_signal(self, dframe):

        signal = 0

        # BUY if Kama fast crosses above kama slow
        if dframe['kama_fast'].iloc[-1] > dframe['kama_slow'].iloc[-1] and dframe['kama_fast'].iloc[-2] <= dframe['kama_slow'].iloc[-2]:
            signal = 1
        # SELL if Kama fast crosses below kama slow
        elif dframe['kama_fast'].iloc[-1] < dframe['kama_slow'].iloc[-1] and dframe['kama_fast'].iloc[-2] >= dframe['kama_slow'].iloc[-2]:
            signal = -1

        return (signal, dframe['close'].iloc[-1]- dframe['kama_fast'].iloc[-1])


    def run(self):

        self.add_kama_fast()
        self.add_kama_slow()
        signal = self.determine_signal(self.df)
        return signal, self.df

    '''
       The following methods are for plotting.
       '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 31  # where the current window will stop (exclusive of the element at this index)

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
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-31:])[0]

    def plot_graph(self):

        # deep copy of data so original is not impacted
        plot_df = self.df.copy(deep=True)

        # determine all signals for the dataset
        self.find_all_signals(plot_df)

        # zero line series for horizontal axis at value 0 in bull power and bear power
        plot_df['zero_line'] = 0

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of senkou span A and B to form the ichimoku cloud, and the parabolic sar dots
        visualisation.add_subplot(plot_df['kama_fast'], color="red")
        visualisation.add_subplot(plot_df['kama_slow'], color="blue")

        # create final plot with title
        visualisation.plot_graph("KAMA Crossover Strategy")
