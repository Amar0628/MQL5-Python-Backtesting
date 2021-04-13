import pandas as pd
import ta
import trading_strategies.visualise as v

'''
This strategy uses the Williams%R Indicator and the stochastic signal line to determine buy and sell signals.
Results are compared for a 5 candle period, using williams indicator values of less than -65 for buy and greater
than -35 for sell, and less than or equal to 35 on the stochastic signal line to buy and greater than or equal to
65 to sell.

@author: Caitlin
'''


class WilliamsStochastic:
    def __init__(self, file_path):
        self.max_window = 35  # comment out if issues with running unit tests
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    # Calculate the williams indicator
    def calculate_williams_indicator(self):
        will_ind = ta.momentum.WilliamsRIndicator(high=self.high, low=self.low, close=self.close)
        self.df['williams_indicator'] = will_ind.wr()

    # Calculate the stochastic signal line
    def calculate_stochastic_signal_line(self):
        stoch_signal = ta.momentum.StochasticOscillator(high=self.high, low=self.low, close=self.close)
        self.df['stoch_signal'] = stoch_signal.stoch_signal()

    def determine_signal(self, dframe):
        # initialise all signals to hold: 0
        dframe['signal'] = 0

        # BUY SIGNAL: signal line is less than or equal to 35 and williams indicator is less than -65 within the last 5 candles
        dframe.loc[(((dframe['stoch_signal'] <= 35) | (dframe['stoch_signal'].shift(1) <= 35) | (
                dframe['stoch_signal'].shift(2) <= 35)
                     | (dframe['stoch_signal'].shift(3) <= 35) | (dframe['stoch_signal'].shift(4) <= 35) | (
                             dframe['stoch_signal'].shift(5) <= 35))
                    & ((dframe['williams_indicator'].shift(2) < -65) | (dframe['williams_indicator'].shift(1) < -65)
                       | (dframe['williams_indicator'] < -65) | (dframe['williams_indicator'].shift(3) < -65)
                       | (dframe['williams_indicator'].shift(4) < -65) | (
                               dframe['williams_indicator'].shift(5) < -65))), 'signal'] = 1

        # SELL SIGNAL: signal line is greater than or equal to 65 and williams indicator is greater than -35 within the last 5 candles
        dframe.loc[(((dframe['stoch_signal'] >= 65) | (dframe['stoch_signal'].shift(1) >= 65) | (
                dframe['stoch_signal'].shift(2) >= 65)
                     | (dframe['stoch_signal'].shift(3) >= 65) | (dframe['stoch_signal'].shift(4) >= 65) | (
                             dframe['stoch_signal'].shift(5) >= 65))
                    & ((dframe['williams_indicator'].shift(2) > -35) | (dframe['williams_indicator'].shift(1) > -35)
                       | (dframe['williams_indicator'] > -35) | (dframe['williams_indicator'].shift(3) > -35) | (
                               dframe['williams_indicator'].shift(4) > -35)
                       | (dframe['williams_indicator'].shift(5) > -35))), 'signal'] = -1

        # return final data point's signal and value of stochastic signal
        signal_col = dframe.columns.get_loc('signal')
        return (dframe.iloc[-1, signal_col], dframe['stoch_signal'].iloc[-1])

    def run_williams_stochastic(self):
        self.calculate_williams_indicator()
        self.calculate_stochastic_signal_line()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1 * len(
            plot_df)  # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 60  # where the current window will stop (exclusive of the element at this index)

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

            # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-60:])[0]

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

        line_35 = [35] * self.max_window
        line_65 = [65] * self.max_window
        line_n35 = [-35] * self.max_window
        line_n65 = [-65] * self.max_window

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(plot_df['stoch_signal'], panel=1, color="orange", ylabel="Stochastic\nSignal Line")
        visualisation.add_subplot(plot_df['williams_indicator'], panel=2, color="blue", ylabel="Williams%R\nIndicator")
        visualisation.add_subplot(line_35, panel=1, width=0.75, secondary_y=False)
        visualisation.add_subplot(line_65, panel=1, width=0.75, secondary_y=False)
        visualisation.add_subplot(line_n35, panel=2, width=0.75, secondary_y=False)
        visualisation.add_subplot(line_n65, panel=2, width=0.75, secondary_y=False)

        # create final plot with title
        visualisation.plot_graph("Williams Stochastic Trading Strategy")

#strategy = WilliamsStochastic(r"C:\Users\Wilson\Documents\INFO3600\info3600_group1-project\back_testing\3yr_historical_data\3YR_AUD_USD\FXCM_AUD_USD_H4.csv")
#strategy.run_williams_stochastic()
#strategy.plot_graph()
