import pandas as pd
import ta
import trading_strategies.visualise as v


'''
@author: Caitlin
This strategy combines the keltner channels, with the stochastic signal line.

'''


class KeltnerStochastic:

    def __init__(self, file_path):
        #self.max_window = 100  #uncomment for graphing purposes
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

    def calculate_stochastic_signal_line(self):
        stoch_signal = ta.momentum.StochasticOscillator(high=self.high, low=self.low, close=self.close)
        self.df['stoch_signal'] = stoch_signal.stoch_signal()


    def determine_signal(self, dataframe):

        # initialise all signals to hold: 0
        action = 0

        # BUY SIGNAL: candle close is below lower keltner band, stochastic signal is <=30, psar is below the candle
        if dataframe['high'].iloc[-1] < dataframe['k_band_lower'].iloc[-1] and dataframe['stoch_signal'].iloc[-1] < 30:
            action = 1

        # SELL SIGNAL: candle close above upper keltner band, stochastic signal >= 70, psar below candle
        elif dataframe['low'].iloc[-1] > dataframe['k_band_upper'].iloc[-1] and dataframe['stoch_signal'].iloc[-1] > 70:
            action = -1


        extra = dataframe['stoch_signal'].iloc[-1]
        return (action, extra)

    def run_keltner_stochastic(self):

        self.calculate_band_lower()
        self.calculate_band_upper()
        self.calculate_stochastic_signal_line()
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

        visualisation.add_subplot(plot_df['stoch_signal'], panel=1, color="blue")
        visualisation.add_subplot(line_70, panel=1, color="green")
        visualisation.add_subplot(line_30, panel=1, color="black")
        visualisation.add_subplot(plot_df['k_band_upper'])
        visualisation.add_subplot(plot_df['k_band_lower'])

        # create final plot with title
        visualisation.plot_graph("Keltner Stochastic Trading Strategy")