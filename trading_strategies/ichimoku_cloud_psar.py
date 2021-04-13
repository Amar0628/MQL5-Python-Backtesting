import pandas as pd 
import ta
import trading_strategies.visualise as v

'''
The Ichimoku Cloud and Parabolic SAR trading strategy determines optimal entry and exit points by looking at the direction of trend, any changes in this direction, along with potential current and future support and resistance points.

Author: Cheryl
'''

class IchimokuCloudPsar:
	def __init__(self, file_path):
		self.max_window = 180 # Set to 180 for graphing trend, MIN value: 78
		self.df = pd.read_csv(file_path)[-self.max_window:]
		self.high = self.df['high']
		self.low = self.df['low']
		self.close = self.df['close']

	# Calculate Parabolic SAR for each data point and store in additional column in dataframe
	def calculate_psar(self):
		indicator_psar = ta.trend.PSARIndicator(high = self.high, low = self.low, close = self.close)
		self.df['sar'] = indicator_psar.psar()

	# Calculate the Tenkan-sen (Conversion Line)	
	def calculate_tenkan_sen(self):
		period_9_high = self.high.rolling(window = 9).max()
		period_9_low = self.low.rolling(window = 9).min()
		self.df['tenkan_sen_line'] = (period_9_high + period_9_low) / 2
		

	# Calculate the Kijun-sen (Base Line)
	def calculate_kijun_sen(self):
		period_26_high = self.high.rolling(window = 26).max()
		period_26_low = self.low.rolling(window = 26).min()
		self.df['kijun_sen_line'] = (period_26_high + period_26_low) / 2

	# The following 2 functions compute values required to create the Komu CLoud (the space between Senkou Span A and Senkou Span B).
	# It represents potential current and future support and resistence points.]

	# Calculate the Senkou Span A (Leading Span A), which makes up one of the boundaries of the Komu Cloud.
	def calculate_senkou_span_A(self):
		self.df['senkou_span_A'] = ((self.df['tenkan_sen_line'] + self.df['kijun_sen_line']) / 2).shift(26)

	# calculate the Senkou Span B (Leading Span B), which makes up the other boundary of the Komu Cloud.
	def calculate_senkou_span_B(self):
		period_52_high = self.high.rolling(window = 52).max()
		period_52_low = self.low.rolling(window = 52).min()
		self.df['senkou_span_B'] = ((period_52_high + period_52_low) / 2).shift(26)

	# Calculate the Chikou Span (Lagging Span)
	def calculate_chikou_span(self):
		self.df['chikou_span'] = self.close.shift(-26)

	def determine_signal(self, dframe):
		action = 0
		# BUY CRITERIA: price is above the Komu cloud and parabolic SAR is below the price
		if dframe['close'].iloc[-1] > dframe['senkou_span_A'].iloc[-1] and dframe['close'].iloc[-1] > dframe['senkou_span_B'].iloc[-1] and dframe['close'].iloc[-1] > dframe['sar'].iloc[-1]:
			action = 1

		# SELL CRITERIA: price is below the Komu cloud and parabolic SAR is above the price
		elif dframe['close'].iloc[-1] < dframe['senkou_span_A'].iloc[-1] and dframe['close'].iloc[-1] < dframe['senkou_span_B'].iloc[-1] and dframe['close'].iloc[-1] < dframe['sar'].iloc[-1]:
			action = -1
		
		# Return final data point's signal
		psar_dist = dframe['sar'].iloc[-1] - dframe['close'].iloc[-1]
		return (action, psar_dist)

	# Run the Ichimoku Cloud with Parabolic SAR trading strategy
	def run_ichimoku_cloud(self):
		self.calculate_psar()
		self.calculate_tenkan_sen()
		self.calculate_kijun_sen()
		self.calculate_senkou_span_A()
		self.calculate_senkou_span_B()
		self.calculate_chikou_span()
		signal = self.determine_signal(self.df)
		return signal

	'''
	The following methods are for plotting.
	'''

	def find_all_signals(self, plot_df):
		# assign intitial value of hold
		plot_df['signal'] = 0

		start = -1*len(plot_df) # using negative indices just in case you are using a subset of input data where index does not start at index 0
		end = start + 78 # where the current window will stop (exclusive of the element at this index)
		
		# loop through data to determine all signals
		while end < 0:
			curr_window = plot_df[start:end]
			action = self.determine_signal(curr_window)[0]
			plot_df.loc[plot_df.index[end - 1], 'signal'] = action
			end += 1
			start += 1 

		# compute final signal
		plot_df.loc[plot_df.index[-1], 'signal'] = self.determine_signal(plot_df[-78:])[0]
		
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

		# add subplots of senkou span A and B to form the ichimoku cloud, and the parabolic sar dots
		visualisation.add_subplot(plot_df['senkou_span_A'], color="royalblue")
		visualisation.add_subplot(plot_df['senkou_span_B'], color="cadetblue")
		visualisation.add_subplot(plot_df['sar'], color="grey", marker = ".", type = "scatter")
		
		# create final plot with title
		visualisation.plot_graph("Ichimoku Cloud and Parabolic SAR Strategy")
		





