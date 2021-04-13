import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The Awesome Oscillator Zero Crossover strategy signals buying and selling opportunities when the Awesome Oscillator (AO) crosses to above or below 0.
When the AO crosses above 0, we wait for 3 consecutive increasing values of AO to confirm bullish movement and then buy. 
When the AO crosses below 0, we wait for 3 consecutive decreasing values of AO to confirm bearish movement and then sell.

Author: Cheryl
'''
class AwesomeOscillatorZeroCrossover:
    def __init__(self, file_path):
        self.max_window = 134 # set to 134 for graphing purposes. Need minimum 37
        self.df = pd.read_csv(file_path)[-self.max_window:]
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    def calculate_awesome_oscillator(self):
        # initialise Awesome Oscillator
        awes_osc = ta.momentum.AwesomeOscillatorIndicator(high = self.high, low = self.low)
        # Calculate
        self.df['awesome_oscillator'] = awes_osc.ao()

    def determine_signal(self, dframe):
        action = 0

        # SELL CRITERIA: awesome oscillator crosses from above to below the zero line, followed by 3 decreasing values
        if dframe['awesome_oscillator'].iloc[-4] >= 0 and dframe['awesome_oscillator'].iloc[-3] <= 0 and \
            dframe['awesome_oscillator'].iloc[-2] < dframe['awesome_oscillator'].iloc[-3] and \
            dframe['awesome_oscillator'].iloc[-1] < dframe['awesome_oscillator'].iloc[-2]:
            action = -1

        # BUY CRITERIA: awesome oscillator crosses from below to above the zero line, followed by 3 increasing values
        elif dframe['awesome_oscillator'].iloc[-4] <= 0 and dframe['awesome_oscillator'].iloc[-3] >= 0 and \
            dframe['awesome_oscillator'].iloc[-2] > dframe['awesome_oscillator'].iloc[-3] and \
            dframe['awesome_oscillator'].iloc[-1] > dframe['awesome_oscillator'].iloc[-2]:
            action = 1

        return (action, dframe['awesome_oscillator'].iloc[-1])

    def run_awesome_oscillator_zero_crossover(self):
        self.calculate_awesome_oscillator()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''
    def find_all_signals(self, plot_df):
         # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 37 # where the current window will stop (exclusive of the element at this index)
        
        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1 

        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-37:])[0]
        
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

        # add subplot of awesome oscillator
        visualisation.add_subplot(plot_df['awesome_oscillator'], type="bar", panel = 1, ylabel="Awesome\nOscillator")
        
        # create final plot with title
        visualisation.plot_graph("Awesome Oscillator Zero Line Crossover Strategy")