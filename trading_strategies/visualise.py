import mplfinance as mpf
import pandas as pd
import numpy as np

'''
This Visualise class is used to create plots for the trading strategies in our library. Use it by instantiating the class, and calling the desired methods.

Author: Cheryl
'''

class Visualise:
	def __init__(self, plot_df):
		self.plot_df = plot_df
		self.subplots = []
		self.range = max(self.plot_df['high']) - min(self.plot_df['low'])
		self.plot_df.index = pd.to_datetime(self.plot_df.datetime) # if your data uses column name date, change this line to pd.to_datetime(self.plot_df.date)

	def add_subplot(self,series, **kwargs):
		self.subplots.append(mpf.make_addplot(series, **kwargs))

	def determine_buy_marker(self):
		self.plot_df['buy_marker'] = np.nan
		# get index of first buy example in input dataset
		buy_index_ls = self.plot_df.index[(self.plot_df['signal'] == 1)].tolist()

		# if a buy example exists
		for i in buy_index_ls:
			self.plot_df.loc[i, 'buy_marker'] = self.plot_df.loc[i, 'low'] - self.range * 0.06
			#break # comment out this break if you would like to see all buy signals

	def determine_sell_marker(self):
		self.plot_df['sell_marker'] = np.nan
		# get index of first sell example in input dataset
		sell_index_ls = self.plot_df.index[(self.plot_df['signal'] == -1)].tolist()
		# if sell example exists
		for i in sell_index_ls:
			self.plot_df.loc[i, 'sell_marker'] = self.plot_df.loc[i, 'high'] + self.range * 0.06
			#break # comment out this break if you would like to see all sell signals

	def plot_graph(self, name):
		# add buy and sell marker if they exist
		if not self.plot_df['buy_marker'].isnull().all():
			self.subplots.append(mpf.make_addplot(self.plot_df['buy_marker'], type = "scatter", marker="^", markersize = 60, color="green"))
		if not self.plot_df['sell_marker'].isnull().all():
			self.subplots.append(mpf.make_addplot(self.plot_df['sell_marker'], type = "scatter", marker="v", markersize = 60, color="red"))

		# Create colour style candlestick colours to green and red
		mc = mpf.make_marketcolors(up='g',down='r')

		# Set colour and grid style
		s  = mpf.make_mpf_style(marketcolors=mc)

		 # view plot
		mpf.plot(self.plot_df, type="candle", addplot=self.subplots, style=s, title=name)
