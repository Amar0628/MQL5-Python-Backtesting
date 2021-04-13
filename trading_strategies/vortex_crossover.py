import pandas as pd
import ta
import trading_strategies.visualise as v

# Source: https://school.stockcharts.com/doku.php?id=technical_indicators:vortex_indicator

class VortexCrossover:
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    def calculate_vortex(self):
        # calculate -VI
        self.df['-vi'] = ta.trend.VortexIndicator(high=self.high, low=self.low, close=self.close,window=14).vortex_indicator_neg()
        # calculate +VI
        self.df['+vi'] = ta.trend.VortexIndicator(high=self.high, low=self.low, close=self.close, window=14).vortex_indicator_pos()


    def determine_signal(self, dframe):
        action = 0
        # BUY CRITERIA: +vi crosses above -vi
        if dframe['+vi'].iloc[-1] > dframe['-vi'].iloc[-1] and dframe['+vi'].iloc[-2] <= dframe['-vi'].iloc[-2]:
            action = 1
        # SELL CRITERIA: -vi crosses above +vi
        elif dframe['+vi'].iloc[-1] < dframe['-vi'].iloc[-1] and dframe['+vi'].iloc[-2] >= dframe['-vi'].iloc[-2]:
            action = -1
        return (action, dframe['close'].iloc[-1])

    def run(self):
        self.calculate_vortex()
        signal = self.determine_signal(self.df)
        return signal, self.df

    '''
    The following methods are for plotting.
    '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 16  # where the current window will stop (exclusive of the element at this index)

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
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-16:])[0]

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
        visualisation.add_subplot(plot_df['+vi'], panel = 1, color="green", width=1, ylabel='VI')
        visualisation.add_subplot(plot_df['-vi'], panel = 1, color="red", width=1)

        # create final plot with title
        visualisation.plot_graph("Vortex Crossover Strategy")
