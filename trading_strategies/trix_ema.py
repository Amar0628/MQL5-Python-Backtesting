import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The TRIX and EMA strategy uses the TRIX indicator (a triple smoothed 30 period EMA) and a Signal Line (9 period EMA of TRIX).
The criteria to buy is when TRIX crosses above the signal line while negative.
The criteria to sell is when TRIX crosses to below the signal line while positive.

Author: Cheryl
'''
class TrixEma:
	def __init__(self, file_path):
		self.max_window = 180 # set to 180 for better understanding of trend in graph. MIN value 99
		self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
	
	def calculate_trix(self):
		# initialise TRIX indicator for n = 30
		indicator_trix = ta.trend.TRIXIndicator(close = self.df['close'], window = 30)
		# calculate values
		self.df['trix'] = indicator_trix.trix() 

	# signal line: 9 period EMA of TRIX  
	def calculate_signal_line(self):
		# initialise EMA indicator for n = 9
		indicator_ema = ta.trend.EMAIndicator(close = self.df['trix'], window = 9)
		# calculate values
		self.df['signal_line'] = indicator_ema.ema_indicator()
	
	def determine_signal(self, dframe):
		action = 0
		trix_signal_dist = dframe['trix'].iloc[-1] - dframe['signal_line'].iloc[-1]
		# BUY CRITERIA: TRIX crosses to above the signal line (9 EMA) while below zero
		if dframe['trix'].iloc[-1] < 0 and dframe['trix'].iloc[-2] < dframe['signal_line'].iloc[-2] and dframe['trix'].iloc[-1] > dframe['signal_line'].iloc[-1]:
			action = 1
		# SELL CRITERIA: TRIX crosses to below the signal line (9 EMA) while above zero
		elif dframe['trix'].iloc[-1] > 0 and dframe['trix'].iloc[-2] > dframe['signal_line'].iloc[-2] and dframe['trix'].iloc[-1] < dframe['signal_line'].iloc[-1]:
			action = -1
		
		return (action, trix_signal_dist)

	def run_trix_ema(self):
		self.calculate_trix()
		self.calculate_signal_line()
		signal = self.determine_signal(self.df)
		return signal, self.df

	''' The following methods are for plotting '''

	def find_all_signals(self, plot_df):

		# assign intitial value of hold
		plot_df['signal'] = 0

		start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
		end = start + 99 # where the current window will stop (exclusive of the element at this index)
		
		# loop through data to determine all signals
		while end < 0:
			curr_window = plot_df[start:end]
			action = self.determine_signal(curr_window)[0]
			plot_df.loc[plot_df.index[end - 1], 'signal'] = action
			end += 1
			start += 1 

		# compute final signal
		plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-99:])[0]
		
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

		# add subplots of TRIX and Signal Line
		visualisation.add_subplot(plot_df['signal_line'], color="royalblue", panel = 1, ylabel="Signal Line")
		visualisation.add_subplot(plot_df['trix'], panel=1, color="orange", ylabel="TRIX / Signal Line", secondary_y=False)
		
		# create final plot with title
		visualisation.plot_graph("TRIX and EMA Signal Line Strategy")