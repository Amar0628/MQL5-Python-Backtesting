import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
Larry Connors' 2 period RSI strategy uses mean reversion to provide a short-term buy or sell signal. 
When the price is above the 200 Moving Average, and 2-period RSI is below 10, this is a buy signal
When the price is below the 200 Moving Average, and 2-period RSI is above 90, this is a sell signal
'''

class Rsi2:
	def __init__(self, file_path):
		self.max_window = 400 # set to 400 for better understanding (can see 200sma through a 200 candlestick period)
		self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]

	def calculate_long_ma(self):
		# initialise SMA indicator at 200 periods
		lma_ind = ta.trend.SMAIndicator(close = self.df['close'], window = 200)
		# generate 200 ma
		self.df['200sma'] = lma_ind.sma_indicator()

	def calculate_short_ma(self):
		# initialise SMA indicator at 5 periods
		sma_ind = ta.trend.SMAIndicator(close = self.df['close'], window = 5)
		# generate 200 ma
		self.df['5sma'] = sma_ind.sma_indicator()

	def calculate_rsi(self):
		# initialise RSI indicator
		rsi_ind = ta.momentum.RSIIndicator(close = self.df['close'], window = 2)
		# generate RSI-2
		self.df['rsi2'] = rsi_ind.rsi()

	def determine_signal(self, dframe):
		action = 0
		# Buy when RSI2 between 0 and 10, and price above 200sma but below 5sma
		if dframe['rsi2'].iloc[-1] < 10 and dframe['close'].iloc[-1] > dframe['200sma'].iloc[-1] and dframe['close'].iloc[-1] < dframe['5sma'].iloc[-1]:
			action = 1
		# Sell when RSI2 between 90 and 100, and price below 200sma but above 5sma
		elif dframe['rsi2'].iloc[-1] > 90 and dframe['close'].iloc[-1] < dframe['200sma'].iloc[-1] and dframe['close'].iloc[-1] > dframe['5sma'].iloc[-1]:
			action = -1
		sma_5_dist = dframe['close'].iloc[-1] - dframe['5sma'].iloc[-1]
		sma_200_dist = dframe['close'].iloc[-1] - dframe['200sma'].iloc[-1]
		return (action, sma_5_dist, sma_200_dist)

	def run_rsi2(self):
		self.calculate_long_ma()
		self.calculate_short_ma()
		self.calculate_rsi()
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

		# oversold and overbought horizontal lines for easy identification of RSI criteria
		plot_df['oversold_line'] = 10 
		plot_df['overbought_line'] = 90 

		# initialise visualisation object for plotting
		visualisation = v.Visualise(plot_df)

		# determining one buy signal example for plotting
		visualisation.determine_buy_marker()

		# determining one sell signal example for plotting
		visualisation.determine_sell_marker()

		# add subplots of 200 SMA, RSI-2, 5 SMA, oversold and overbought lines
		visualisation.add_subplot(plot_df['200sma'], color='g')
		visualisation.add_subplot(plot_df['rsi2'], panel = 1, ylabel='RSI-2')
		visualisation.add_subplot(plot_df['5sma'], color='orange')
		visualisation.add_subplot(plot_df['oversold_line'], color='grey', panel = 1, secondary_y = False)
		visualisation.add_subplot(plot_df['overbought_line'], color='grey', panel = 1, secondary_y = False)
		
		# create final plot with title
		visualisation.plot_graph("Larry Connors' RSI-2 Strategy")
		