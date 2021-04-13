import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The Awesome Oscillator Saucers strategy looks for a bullish or bearish saucer pattern in the Awesome Oscillator, where close price is greater than 200 EMA.
A bullish saucer pattern consists of 3 positive AO bars which form the curve of a saucer (i.e. the middle value is smallest).
A bearish saucer patter consists of 3 negative AO bars which form the curve of an upside down saucer (i.e. the middle value is greatest (least negative)).

Author: Cheryl
'''

class AwesomeOscillatorSaucer:
    def __init__(self, file_path):
        self.max_window = 300 # set to 300 for better understanding in plot (can see 200EMA through a 100 candlestick period). MIN value 200
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]

    def calculate_awesome_oscillator(self):
        # initialise Awesome Oscillator
        awes_osc = ta.momentum.AwesomeOscillatorIndicator(high = self.df['high'], low = self.df['low'])
        # Calculate
        self.df['awesome_oscillator'] = awes_osc.ao()

    def calculate_ema(self):
        # initialise EMA indicator for 200 time periods
        indicator_ema = ta.trend.EMAIndicator(close = self.df['close'], window = 200)
        # Calculate
        self.df['200ema'] = indicator_ema.ema_indicator()

    def determine_signal(self, dframe):
        action = 0
        ema_dist = dframe['close'].iloc[-1] - dframe['200ema'].iloc[-1]

        bar_1 = dframe['awesome_oscillator'].iloc[-3]
        bar_2 = dframe['awesome_oscillator'].iloc[-2]
        bar_3 = dframe['awesome_oscillator'].iloc[-1]
        curr_close = dframe['close'].iloc[-1]
        curr_200ema = dframe['200ema'].iloc[-1]
        
        # BUY CRITERIA: CONSECUTIVELY: all 3 bars positive, 2 decreasing awesome oscillator values followed by an increase, and close is above the 200EMA
        if bar_1 > 0 and bar_2 > 0 and bar_3 > 0 and \
            bar_1 > bar_2 and bar_2 < bar_3 and curr_close > curr_200ema:
                action = 1

        # SELL CRITERIA: CONSECUTIVELY: all 3 bars negative, 2 increasing awesome oscillator values followed by a decrease, and close is below the 200EMA
        elif bar_1 < 0 and bar_2 < 0 and bar_3 < 0 and\
            bar_1 < bar_2 and bar_2 > bar_3 and curr_close < curr_200ema:
                action = -1

        return (action, ema_dist)

    def run_awesome_oscillator_saucer(self):
        self.calculate_awesome_oscillator()
        self.calculate_ema()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 200 # where the current window will stop (exclusive of the element at this index)
        
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

        # add subplots of 200ema and awesome oscillator
        visualisation.add_subplot(plot_df['200ema'], color="orange")
        visualisation.add_subplot(plot_df['awesome_oscillator'], type="bar", panel = 1, ylabel="Awesome\nOscillator")
        
        # create final plot with title
        visualisation.plot_graph("Awesome Oscillator Saucers Strategy")