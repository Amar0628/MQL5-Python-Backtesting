import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The Vortex indicator (VI) comprises two oscillators which illustrate positive (+VI) and negative trend movements (-VI).  
We buy when +VI crosses above -VI (indicating a bullish trend) and close price is above 50 SMA.
We sell when -VI crosses above +VI (indicating a bearish trend) and close price is below 50 SMA.

Author: Cheryl
'''

class VortexSma:
	def __init__(self, file_path):
		self.max_window = 150 # set to 100 for better understanding of trend in graph. MIN value 50
		self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
		self.high = self.df['high']
		self.close = self.df['close']
		self.low = self.df['low']
   
	def calculate_sma(self):
		# initialise SMA indicator for 50 time periods
		indicator_sma = ta.trend.SMAIndicator(close = self.close, window = 50)
		# Calculate 50 sma
		self.df['50_sma'] = indicator_sma.sma_indicator()
	
	def calculate_vortex(self):
		# initialise vortex indicator
		indicator_vortex = ta.trend.VortexIndicator(high = self.high, low = self.low, close = self.close, window = 14)
		# calculate -VI
		self.df['-vi'] = indicator_vortex.vortex_indicator_neg()
		# calculate +VI
		self.df['+vi'] = indicator_vortex.vortex_indicator_pos()
	
	def determine_signal(self, dframe):
		sma_dist = dframe['close'].iloc[-1] - dframe['50_sma'].iloc[-1]
		action = 0
		# BUY CRITERIA: +vi crosses above -vi, and price is above 50sma
		if dframe['+vi'].iloc[-2] <= dframe['-vi'].iloc[-2] and dframe['+vi'].iloc[-1] > dframe['-vi'].iloc[-1] and dframe['close'].iloc[-1] > dframe['50_sma'].iloc[-1]:
			action = 1
		# SELL CRITERIA: -vi crosses above +vi, and price is below 50sma
		elif dframe['-vi'].iloc[-2] <= dframe['+vi'].iloc[-2] and dframe['-vi'].iloc[-1] > dframe['+vi'].iloc[-1] and dframe['close'].iloc[-1] < dframe['50_sma'].iloc[-1]:
			action = -1
		return (action, sma_dist)

	def run_vortex_sma(self):
		self.calculate_sma()
		self.calculate_vortex()
		signal = self.determine_signal(self.df)
		return signal, self.df

	''' The following methods are for plotting '''

	def find_all_signals(self, plot_df):
		# assign intitial value of hold
		plot_df['signal'] = 0

		start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
		end = start + 50 # where the current window will stop (exclusive of the element at this index)
		
		# loop through data to determine all signals
		while end < 0:
			curr_window = plot_df[start:end]
			action = self.determine_signal(curr_window)[0]
			plot_df.loc[plot_df.index[end - 1], 'signal'] = action
			end += 1
			start += 1 

		# compute final signal
		plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-50:])[0]
		
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

		# add subplots of 50 SMA, +VI and -VI
		visualisation.add_subplot(plot_df['50_sma'], color="royalblue")
		visualisation.add_subplot(plot_df['+vi'], panel=1, color="seagreen", ylabel="Vortex Indicator")
		visualisation.add_subplot(plot_df['-vi'], panel=1, color="darkred", secondary_y=False)
		
		# create final plot with title
		visualisation.plot_graph("Vortex Indicator and 50 SMA Strategy")