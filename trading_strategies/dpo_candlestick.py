import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The DPO is an indicator designed to remove trend from price and make it easier to identify underlying cycles in price movement. 
When the DPO moves above zero, this indicates a potential bullish trend. On the other hand, when DPO moves below zero, this suggests a bearish sign.
The criteria to buy is when DPO crosses above zero and the candle stick pattern suggests a bullish trend.
The criteria to sell is when DPO crosses below zero and the candle stick pattern suggests a bearish trend.

Author: Cheryl
'''

class DpoCandlestick:
    def __init__(self, file_path):
        self.max_window = 100 # set to 100 for better understanding of trend in graph. MIN value 21
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
    
    def calculate_dpo(self):
        # initialise DPO indicator for n = 20
        indicator_dpo = ta.trend.DPOIndicator(close = self.df['close'], window = 20)
        # calculate values
        self.df['dpo'] = indicator_dpo.dpo() 
    
    def determine_signal(self, dframe):
        action = 0
        candle_length = dframe['close'].iloc[-1] - dframe['open'].iloc[-1]

        curr_close = dframe['close'].iloc[-1]
        prev_close = dframe['close'].iloc[-2]

        curr_open = dframe['open'].iloc[-1]
        prev_open = dframe['open'].iloc[-2]

        # BUY CRITERIA: DPO crosses above 0, and bullish candle stick pattern 
        if dframe['dpo'].iloc[-2] <= 0 and dframe['dpo'].iloc[-1] > 0:
            # Bullish Candlestick pattern 1: piercing line
            if curr_close > curr_open and curr_close > (prev_close + prev_open)/2 and prev_close < prev_open:
                action = 1
            # Bullish Candlestick Pattern 2: Bullish engulfing
            elif prev_close < prev_open and curr_close > curr_open and curr_close > prev_open and curr_open <= prev_close: 
                action = 1

        # SELL CRITERIA: DPO crosses below 0, and bearish candles tick pattern 
        if dframe['dpo'].iloc[-2] >= 0 and dframe['dpo'].iloc[-1] < 0:
            # Bearish Candlestick pattern 1: Dark Cloud Cover
            if prev_close > prev_open and curr_open > curr_close and curr_open > prev_close and curr_close < (prev_close + prev_open)/2:
                action = -1
            # Bearish Candlestick pattern 2: Bearish engulfing
            elif prev_close > prev_open and curr_open > curr_close and curr_close < prev_open and (curr_open - curr_close) > (prev_close - prev_open):
                action = -1

        return (action, candle_length)

    def run_dpo_candlestick(self):
        self.calculate_dpo()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 21 # where the current window will stop (exclusive of the element at this index)
        
        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1 

        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-21:])[0]  
        
    def plot_graph(self):

        # deep copy of data so original is not impacted
        plot_df = self.df.copy(deep=True)

        # add zero line series to show horizontal axis at dpo value of 0
        plot_df['zero_line'] = 0 

        # determine all signals for the dataset
        self.find_all_signals(plot_df)

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of zero line and dpo
        visualisation.add_subplot(plot_df['zero_line'], color="grey", panel=1, secondary_y=False)
        visualisation.add_subplot(plot_df['dpo'], color="royalblue", panel = 1, ylabel="DPO")
        
        # create final plot with title
        visualisation.plot_graph("DPO and Candlestick Pattern Strategy")