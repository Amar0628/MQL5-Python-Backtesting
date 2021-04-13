import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The Elder Ray Index measures the amount of buying and selling power in a market with two indicators: Bull Power and Bear Power. 
This index is used in conjunction with a 13 EMA to further gauge the trend.
We buy when price is above the 13-period exponential moving average, and both EMA and Bear Power is increasing.
We sell when price is below the 13 period exponential moving average, and both EMA and Bull Power is decreasing.

Author: Cheryl
'''
class ElderRayAlternative:
    def __init__(self, file_path):
        self.max_window = 100 # set to 100 for better understanding of trend in graph. MIN value 14
        self.df = pd.read_csv(file_path)[-self.max_window:]
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']
   
    def calculate_ema(self):
        # initialise EMA indicator for 13 time periods
        indicator_ema = ta.trend.EMAIndicator(close = self.close, n = 13)
        # Calculate
        self.df['13_ema'] = indicator_ema.ema_indicator()
    
    def calculate_bull_power(self):
        self.df['bull_power'] = self.df['high'] - self.df['13_ema']

    def calculate_bear_power(self):
        self.df['bear_power'] = self.df['low'] - self.df['13_ema']
        
    
    def determine_signal(self, df):
        action = 0
        ema_dist = df['close'].iloc[-1] - df['13_ema'].iloc[-1]

        # BUY CRITERIA: price is above 13-EMA and both EMA and Bear Power is increasing
        if df['close'].iloc[-1] > df['13_ema'].iloc[-1] and df['13_ema'].iloc[-1] > df['13_ema'].iloc[-2] and df['bear_power'].iloc[-1] > df['bear_power'].iloc[-2]:
            action = 1

        # SELL CRITERIA: price is below 13-EMA and both EMA and Bull Power is decreasing
        elif df['close'].iloc[-1] < df['13_ema'].iloc[-1] and df['13_ema'].iloc[-1] < df['13_ema'].iloc[-2] and df['bull_power'].iloc[-1] < df['bull_power'].iloc[-2]:
            action = -1

        return (action, ema_dist)

    def run_elder_ray(self):
        self.calculate_ema()
        self.calculate_bull_power()
        self.calculate_bear_power()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''
    
    def find_all_signals(self, plot_df):
         # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 14 # where the current window will stop (exclusive of the element at this index)
        
        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1 

        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-22:])[0]

        
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

        # add subplots of 13 ema, bull power, bear power, and zero lines
        visualisation.add_subplot(plot_df['13_ema'], color="royalblue")
        visualisation.add_subplot(plot_df['bull_power'], panel=1, type="bar", ylabel="Bull Power")
        visualisation.add_subplot(plot_df['bear_power'], panel=2, type="bar", ylabel="Bear Power")
        visualisation.add_subplot(plot_df['zero_line'], panel=1, secondary_y=False, color="gray")
        visualisation.add_subplot(plot_df['zero_line'], panel=2, secondary_y=False, color="gray")
        
        # create final plot with title
        visualisation.plot_graph("Elder Ray and 13 EMA Strategy")