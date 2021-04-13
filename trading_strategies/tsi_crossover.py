# -*- coding: utf-8 -*-
"""
@author: vita
https://www.investopedia.com/terms/t/tsi.asp
"""
import pandas as pd
import ta
import trading_strategies.visualise as v



class TSICrossover:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        # self.df = pd.DataFrame(inputs)
        self.close = self.df['close']

    def add_tsi(self):
        self.df['tsi_line'] = ta.momentum.TSIIndicator(close=self.close).tsi()

    def calculate_tsi_signal(self):
        self.df['tsi_signal'] = self.df['tsi_line'].ewm(span=9, adjust=False).mean()

    def determine_signal(self, dframe):
        line = dframe['tsi_line']
        signal = dframe['tsi_signal']

        action = 0

        # SELL CRITERIA: if TSI line and signal line has crossed above 0 and TSI line crosses signal
        if (line.iloc[-1] > 0 and signal.iloc[-1] > 0 and line.iloc[-2] > 0 and signal.iloc[-2] > 0) and \
                ((line.iloc[-1] < signal.iloc[-1] and line.iloc[-2] > signal.iloc[-2]) or (
                        line.iloc[-1] > signal.iloc[-1] and line.iloc[-2] < signal.iloc[-2])):
            action = -1

        # BUY CRITERIA: if TSI line and signal line is below 0 and tsi crosses signal line
        if (line.iloc[-1] < 0 and signal.iloc[-1] < 0 and line.iloc[-2] < 0 and signal.iloc[-2] < 0) and \
                ((line.iloc[-1] > signal.iloc[-1] and line.iloc[-2] < signal.iloc[-2]) or (
                        line.iloc[-1] < signal.iloc[-1] and line.iloc[-2] > signal.iloc[-2])):
            action = 1

        return action, line.iloc[-1] - signal.iloc[-1],

    def run_tsi_crossover(self):
        self.add_tsi()
        self.calculate_tsi_signal()
        return self.determine_signal(self.df)

    ''' The following methods are for plotting '''
    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 40

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-40:])[0]
        plot_df.loc[plot_df.index[-1], 'signal'] = action

    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)

        self.find_all_signals(plot_df)

        plot_df['0_line'] = 0

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(plot_df['tsi_line'], panel=1, color='b', width=0.75, ylabel='TSI Line\n (blue)')
        visualisation.add_subplot(plot_df['tsi_signal'], panel=1, color='pink', width=0.75, ylabel='TSI Signal\n (pink)')
        visualisation.add_subplot(plot_df['0_line'], panel=1, color='k', secondary_y=False, width=0.75, linestyle='solid')

        # create final plot with title
        visualisation.plot_graph("TSI Crossover Strategy")

