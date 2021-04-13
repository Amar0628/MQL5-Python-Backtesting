import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The RSI 80-20 strategy uses the RSI indicator with smoothing period 8 to be more responsive.
TO BUY:
if there is a low candle with rsi <= 20, where later is a lower candle with higher RSI (divergence), 
enter (buy) at the next candle which closes above our first identified low candle. 
TO SELL:
if there is a high candle with rsi >= 80, where later is a higher candle with lower RSI (divergence),
enter (sell) at the next candle which closes below our first identified high candle.
'''

class Rsi8020:
    def __init__(self, file_path):
        self.max_window = 100 # 100 for plotting purposes - to see general trend - minimum needed is 50 + waiting_period 
        self.waiting_period = 5 # how long you are willing to wait to enter after finding the lowest low in last 50 
        #self.df = pd.read_csv(file_path, index_col=0)[-self.max_window:]
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]

    def calculate_rsi(self):
        # initiate rsi indicator
        indicator_rsi = ta.momentum.RSIIndicator(close = self.df['close'], window = 8)
        # calculate rsi
        self.df['rsi'] = indicator_rsi.rsi()

    def determine_signal(self, dframe):
        action = 0
        candles_window = dframe[-50-self.waiting_period:-3] 

        # BUY CRITERIA
        # 1. Find lowest low in candle window
        if candles_window.close.min() < candles_window.open.min():
            lowest_low = candles_window[candles_window.close == candles_window.close.min()]
        else:
            lowest_low = candles_window[candles_window.open == candles_window.open.min()]
        
        # 2. Check if lowest low has RSI <= 20 and didn't happen too early (more than number of waiting periods before)

        if lowest_low['rsi'].iloc[-1] <= 20 and dframe.tail(1).index[0] - lowest_low.index.values.astype(int)[0] <= self.waiting_period:
            divergence = False 
            first_higher = False

            # Check for subsequent divergence in waiting period 
            i = lowest_low.index.values.astype(int)[0] - dframe.tail(1).index[0]
            while i < -1:
                # find a candle that has a lower low but higher rsi - divergence
                if dframe['low'].iloc[i] < lowest_low['low'].iloc[-1] and dframe['rsi'].iloc[i] > lowest_low['rsi'].iloc[-1]:
                    divergence = True
                    divergent_point = dframe.index.values.astype(int)[i]
                    break
                i += 1

            # 2nd last candle must close higher than 50 candle low: 
            if divergence and dframe['close'].iloc[-2] > lowest_low['close'].iloc[-1]:
                first_higher = True
                # check if any previous candles closed higher 
                i = max(-self.waiting_period, divergent_point - dframe.tail(1).index[0])  # start from right after divergence or beginning of waiting period
                while i > max(-self.waiting_period, divergent_point - dframe.tail(1).index[0] ):
                    if dframe['close'].iloc[i] > lowest_low['close'].iloc[-1]:
                        first_higher = False 
                        break
                    i -= 1

            # both conditions satisfied for buy criteria
            if divergence and first_higher:
                action = 1
        
        # SELL CRITERIA
        # 1. Find highest high in candle window
        if candles_window.close.max() > candles_window.open.max():
            highest_high = candles_window[candles_window.close == candles_window.close.max()]
        else:
            highest_high = candles_window[candles_window.open == candles_window.open.max()]

        # 2. Check if lowest low has RSI >= 80 and didn't happen too early (more than number of waiting periods before)
        if highest_high['rsi'].iloc[-1] >= 80 and dframe.tail(1).index[0] - highest_high.index.values.astype(int)[0] <= self.waiting_period:
            divergence = False 
            first_lower = False

            # Check for subsequent divergence in waiting period
            i = highest_high.index.values.astype(int)[0] - dframe.tail(1).index[0]
            while i < -1:
                # find a candle that has a higher high but lower rsi - divergence
                if dframe['high'].iloc[i] > highest_high['high'].iloc[-1] and dframe['rsi'].iloc[i] < highest_high['rsi'].iloc[-1]:
                    divergence = True
                    divergent_point = dframe.index.values.astype(int)[i]
                    break
                i += 1

            # 2nd last candle must close higher than 50 candle high: 
            if divergence and dframe['close'].iloc[-2] > highest_high['close'].iloc[-1]:
                first_lower = True
                # check if any previous candles closed higher 
                i = max(-self.waiting_period, divergent_point - dframe.tail(1).index[0]) 
                while i > max(-self.waiting_period, divergent_point - dframe.tail(1).index[0] ):
                    if dframe['close'].iloc[i] > highest_high['close'].iloc[-1]:
                        first_lower = False 
                        break
                    i -= 1
                    
            # both conditions satisfied for buy criteria
            if divergence and first_lower:
                action = -1

        return (action, dframe['rsi'].iloc[-1])


    def run_rsi_80_20(self):
        self.calculate_rsi()
        signal = self.determine_signal(self.df)
        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        
        # assign intitial value of hold
        plot_df['signal'] = 0

        start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
        end = start + 50 + self.waiting_period # where the current window will stop (exclusive of the element at this index)
        
        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1 
        
        # compute final signal
        plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-(50 + self.waiting_period):])[0]
    
    def plot_graph(self):

        # deep copy of data so original is not impacted
        plot_df = self.df.copy(deep=True)

        self.find_all_signals(plot_df)
       
           # preparing values for horizontal line at rsi values 80 and 20 for visual purposes
        plot_df['80_line'] = 80
        plot_df['20_line'] = 20

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots of RSI, 80 line and 20 line
        visualisation.add_subplot(plot_df['rsi'], panel=1, ylabel="RSI-8")
        visualisation.add_subplot(plot_df['80_line'], panel=1, secondary_y=False)
        visualisation.add_subplot(plot_df['20_line'], panel=1, secondary_y=False)
        
        # create final plot with title
        visualisation.plot_graph("RSI 80-20 Strategy")