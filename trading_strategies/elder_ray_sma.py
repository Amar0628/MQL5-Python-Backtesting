import pandas as pd 
import ta
import mplfinance as mpf
import numpy as np

'''
The Elder Ray Index measures the amount of buying and selling power in a market with two indicators: Bull Power and Bear Power. 
This index is used in conjunction with a 13 EMA and 5 SMAto further gauge the trend.
We buy when Bear Power is negative but increasing, Bull Power is increasing, EMA is positively sloped and close price is above SMA.
We sell when Bull Power is positive but decreasing, Bear Power is decreasing, EMA is negatively sloped and close price is below SMA.

Author: Cheryl
'''
class ElderRaySma:
	def __init__(self, file_path):
		self.max_window = 100 # set to 100 for better understanding of trend in graph. MIN value 14
		self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))[-self.max_window:]
		self.high = self.df['high']
		self.close = self.df['close']
		self.low = self.df['low']
   
	def calculate_ema(self):
		# initialise EMA indicator for 13 time periods
		indicator_ema = ta.trend.EMAIndicator(close = self.close, window = 13)
		# Calculate
		self.df['13_ema'] = indicator_ema.ema_indicator()

	def calculate_sma(self):
		# initialise SMA indicator for 5 time periods
		indicator_sma = ta.trend.SMAIndicator(close = self.close, window = 5)
		# Calculate 5 sma
		self.df['5_sma'] = indicator_sma.sma_indicator()
	
	def calculate_bull_power(self):
		self.df['bull_power'] = self.df['high'] - self.df['13_ema']

	def calculate_bear_power(self):
		self.df['bear_power'] = self.df['low'] - self.df['13_ema']
		
	
	def determine_signal(self):
		action = 0
		ema_dist = self.df['close'].iloc[-1] - self.df['13_ema'].iloc[-1]

		# BUY CRITERIA: Bear power’s value is negative but increasing, Bull power’s value is increasing and 13 EMA is increasing. AND price is greater than 5 sma
		if self.df['bear_power'].iloc[-1] < 0 and self.df['bear_power'].iloc[-1] > self.df['bear_power'].iloc[-2] \
			and self.df['bull_power'].iloc[-1] > self.df['bull_power'].iloc[-2] and self.df['13_ema'].iloc[-1] > self.df['13_ema'].iloc[-2] \
				and self.df['close'].iloc[-1] > self.df['5_sma'].iloc[-1]:
			action = 1

		# SELL CRITERIA: Bull power’s value is positive but decreasing,  Bear power’s value is decreasing and 13 EMA is decreasing. AND price is less than 5 sma
		elif self.df['bull_power'].iloc[-1] > 0 and self.df['bull_power'].iloc[-1] < self.df['bull_power'].iloc[-2] \
			and self.df['bear_power'].iloc[-1] < self.df['bear_power'].iloc[-2] and self.df['13_ema'].iloc[-1] < self.df['13_ema'].iloc[-2] \
				and self.df['close'].iloc[-1] < self.df['5_sma'].iloc[-1]:
			action = -1

		return (action, ema_dist)

	def run_elder_ray(self):
		self.calculate_sma()
		self.calculate_ema()
		self.calculate_bull_power()
		self.calculate_bear_power()
		signal = self.determine_signal()
		return signal, self.df