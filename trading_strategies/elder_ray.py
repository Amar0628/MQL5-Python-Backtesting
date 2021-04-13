import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The Elder Ray Index measures the amount of buying and selling power in a market with two indicators: Bull Power and Bear Power. 
This index is used in conjunction with a 21 EMA to further gauge the trend.
We buy when Bear Power is negative but increasing, Bull Power is increasing and EMA is positively sloped.
We sell when Bull Power is positive but decreasing, Bear Power is decreasing and EMA is negatively sloped.

Author: Cheryl
'''
class ElderRay:
    def __init__(self, file_path):
        self.max_window = 100 # set to 100 for better understanding of trend in graph. MIN value 22
        self.df = pd.read_csv(file_path)[-self.max_window:]
   
    def calculate_ema(self):
        # initialise EMA indicator for 21 time periods
        indicator_ema = ta.trend.EMAIndicator(close = self.df['close'], n = 21)
        # Calculate
        self.df['21_ema'] = indicator_ema.ema_indicator()
    
    def calculate_bull_power(self):
        self.df['bull_power'] = self.df['high'] - self.df['21_ema']

    def calculate_bear_power(self):
        self.df['bear_power'] = self.df['low'] - self.df['21_ema']
        
    def determine_signal(self, dframe):
        action = 0
        ema_dist = dframe['close'].iloc[-1] - dframe['21_ema'].iloc[-1]

        # BUY CRITERIA: Bear power’s value is negative but increasing, Bull power’s value is increasing and 21 EMA is increasing.
        if dframe['bear_power'].iloc[-1] < 0 and dframe['bear_power'].iloc[-1] > dframe['bear_power'].iloc[-2] \
            and dframe['bull_power'].iloc[-1] > dframe['bull_power'].iloc[-2] and dframe['21_ema'].iloc[-1] > dframe['21_ema'].iloc[-2] :
            action = 1

        # SELL CRITERIA: Bull power’s value is positive but decreasing,  Bear power’s value is decreasing and 21 EMA is decreasing.
        elif dframe['bull_power'].iloc[-1] > 0 and dframe['bull_power'].iloc[-1] < dframe['bull_power'].iloc[-2] \
            and dframe['bear_power'].iloc[-1] < dframe['bear_power'].iloc[-2] and dframe['21_ema'].iloc[-1] < dframe['21_ema'].iloc[-2] :
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
        end = start + 22 # where the current window will stop (exclusive of the element at this index)
        
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

        # add subplots of 21 ema, bull power, bear power, and zero lines
        visualisation.add_subplot(plot_df['21_ema'], color="royalblue")
        visualisation.add_subplot(plot_df['bull_power'], panel=1, type="bar", ylabel="Bull Power")
        visualisation.add_subplot(plot_df['bear_power'], panel=2, type="bar", ylabel="Bear Power")
        visualisation.add_subplot(plot_df['zero_line'], panel=1, secondary_y=False, color="gray")
        visualisation.add_subplot(plot_df['zero_line'], panel=2, secondary_y=False, color="gray")
        
        # create final plot with title
        visualisation.plot_graph("Elder Ray and 21 EMA Strategy")