import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The Parabolic SAR + Moving Averages trading strategy determines entry points by identifying any reversals in trend. 
A short (20 period) and long (40 period) simple moving average helps to determine whether a reversal is happening, and this is verified by the Parabolic SAR indicator.
Criteria to sell:
When the Short Moving Average crosses below the Long Moving Average, we wait for the Parabolic SAR dot to appear above a candlestick.
Then, we sell at the candlestick immediately after.
Criteria to buy:
When the Long Moving Average crosses below the Short Moving Average, we wait for the Parabolic SAR dot to appear below a candlestick.
Then, we buy at the candlestick immediately after.

Author: Cheryl
'''

class PsarMovingAverage:
	def __init__(self, file_path):
		self.waiting_period = 8 # How long you are willing to wait for a reversal parabolic SAR dot
		self.max_window = 120 # set to 120 for plotting purposes (can see sma's through a 80 period timeline) - Min value = 42 + waiting_period
		self.df = pd.read_csv(file_path)[-self.max_window:]

	def calculate_psar(self):
		indicator_psar = ta.trend.PSARIndicator(high = self.df["high"], low = self.df["low"], close = self.df["close"])
		self.df['sar'] = indicator_psar.psar()

	def calculate_20sma(self):
		# Calculate SMA (short window of 20)
		self.df['20sma'] = self.df['close'].rolling(window = 20, min_periods = 20, center = False).mean()
	
	def calculate_40sma(self):
		# Calculate LMA  (long window of 40)
		self.df['40sma'] = self.df['close'].rolling(window = 40, min_periods = 40, center = False).mean()

	def find_crossovers(self):
		# Create a column called 'greater_ma' which indicates which MA is on top. 
		# Assign intiial 'greater_ma' value of all datapoints from the 20th onwards to 0
		self.df['greater_ma'] = 0

		# Assign 'greater_ma' value of 1 if the SMA is less than the LMA for 20 time periods (duration of short window)
		self.df.loc[self.df['20sma'] < self.df['40sma'], 'greater_ma'] = 1
		self.df.loc[:20, 'greater_ma'] = 0

		# A difference if '1' indicates the short (20 period) moving average is crossing below the long (40 period) moving average
		# A difference of '-1' indicates the long (40 period) moving average is crossing below the short (20 period) moving average
		self.df['crossover'] = self.df['greater_ma'].diff()

	def determine_signal(self, dframe):
		action = 0
		sar_dist = dframe['sar'].iloc[-1] - dframe['close'].iloc[-1]

		# BUY CRITERIA
		if dframe['sar'].iloc[-2] < dframe['close'].iloc[-2]:

			# Identify if crossover occured within waiting period
			crossover_occurred = False
			i = -1
			while i >= self.waiting_period * -1:
				if dframe['crossover'].iloc[i-2] == -1:
					crossover_occurred = True
					crossover_i = i-2
					break
				i -= 1

			# Identify if first reversal dot
			if crossover_occurred: 
				first_reversal = True
				i = -2
				while (i-1) > crossover_i:
					if dframe['sar'].iloc[i-1] < dframe['close'].iloc[i-1]:
						first_reversal = False
						break
					i -= 1

				# buy if both conditions satisfied
				if first_reversal and crossover_occurred:
					action = 1

		# SELL CRITERIA
		if dframe['sar'].iloc[-2] > dframe['close'].iloc[-2]:

			# Identify if crossover occured within waiting period
			crossover_occurred = False
			i = -1
			while i >= self.waiting_period * -1:
				if dframe['crossover'].iloc[i-2] == 1:
					crossover_occurred = True
					crossover_i = i-2
					break
				i -= 1

			# Identify if first reversal dot
			if crossover_occurred: 
				first_reversal = True
				i = -2
				while (i-1) > crossover_i:
					if dframe['sar'].iloc[i-1] > dframe['close'].iloc[i-1]:
						first_reversal = False
						break
					i -= 1

				# buy if both conditions satisfied
				if first_reversal and crossover_occurred:
					action = -1
		
		return (action, sar_dist)

	def run_psar_moving_average(self):
		self.calculate_psar()
		self.calculate_20sma()
		self.calculate_40sma()
		self.find_crossovers()

		signal = self.determine_signal(self.df)
		return signal, self.df

	''' The following methods are for plotting '''

	def find_all_signals(self, plot_df):
		# assign intitial value of hold
		plot_df['signal'] = 0

		start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
		end = start + 42 + self.waiting_period # where the current window will stop (exclusive of the element at this index)
		
		# loop through data to determine all signals
		while end < 0:
			curr_window = plot_df[start:end]
			action = self.determine_signal(curr_window)[0]
			plot_df.loc[plot_df.index[end - 1], 'signal'] = action
			end += 1
			start += 1 

		# compute final signal
		plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-(42 + self.waiting_period):])[0]	

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

		# add subplots of 20 SMA, 40 SMA and Parabolic SAR
		visualisation.add_subplot(plot_df['20sma'])
		visualisation.add_subplot(plot_df['40sma'])
		visualisation.add_subplot(plot_df['sar'],marker='.', type="scatter", color='grey')
	
		# create final plot with title
		visualisation.plot_graph("Parabolic SAR and Moving Averages Strategy")		
