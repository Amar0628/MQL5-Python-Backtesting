# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 17:20:00 2020

@author: mingyu guo

The oops signal strategy determines at market open if the opening position signals can be taken advantage of with short stop above the opening price or long stop below the opening price
"""

import datetime
import pandas as pd
import mplfinance as mpf

class OopsSignals:
    
    #loading the data in from file_path
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path, parse_dates=['datetime'])

    # created is_yesterday column to mark all of yesterday's data        
    def mark_yesterday(self):
        current_date = self.df['date'].iloc[-1].to_pydatetime().date()
        yesterday_date = current_date - datetime.timedelta(days=1)
        self.df.loc[self.df['datetime'].dt.date == yesterday_date, 'is_yesterday'] = 1
        
    # Calculates the high of yesterday's market
    def calculate_yesterday_high(self):
        return self.df.loc[self.df['is_yesterday'] == 1, 'high'].max()
        
    # Calculate the low of yesterday's market
    def calculate_yesterday_low(self):
        return self.df.loc[self.df['is_yesterday'] == 1, 'low'].min()
    
    # Find today's opening price
    def calculate_open(self):
        yesterday_closing_index = self.df.loc[self.df['is_yesterday'] == 1].index.max()
        return self.df['open'].iloc[yesterday_closing_index + 1]
        
    def calculate_current_price(self):
        return self.df['close'].iloc[-1]

    def plot_graph(self):
        self.df.index = pd.to_datetime(self.df.datetime)
        self.df = self.df[-150:]
        tcdf = self.df[['bb_low_band','bb_high_band','sma']] #create list of dicts and pass it to the addplot keyword
        apds = [ mpf.make_addplot(tcdf),
                 mpf.make_addplot((self.df['stoch_rsi']), panel = 1, color = 'g')
               ]
        mpf.plot(self.df, type = 'candle', addplot = apds)

    # Runs the oops signal strategy
    def run_oops_signals(self):
        self.mark_yesterday()
        yesterday_high = self.calculate_yesterday_high()
        yesterday_low = self.calculate_yesterday_low()
        opening = self.calculate_open()
        current_price = self.calculate_current_price()
        
        if (opening < yesterday_low) & (current_price < opening):
            return (1, opening)
        elif (opening > yesterday_high) & (current_price > opening):
            return (-1, opening)
        else:
            return (0,None)
        
    