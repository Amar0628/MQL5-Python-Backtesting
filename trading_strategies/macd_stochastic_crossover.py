# -*- coding: utf-8 -*-
"""
@author: vita
This strategy uses the MACD crossovers and Stochastic crossovers. The stochastic crossover should occur just before the MACD crossover.
https://www.dailyfx.com/forex/education/trading_tips/daily_trading_lesson/2020/02/11/macd-vs-stochastic.html
"""
import pandas as pd
import ta
import trading_strategies.visualise as v



class MACDStochasticCrossover:
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        # self.df = pd.DataFrame(inputs)
        self.close = self.df['close']
        self.high = self.df['high']
        self.low = self.df['low']

    # calculates the macd line
    def add_macd_line(self):
        self.df['macd_line'] = ta.trend.MACD(close=self.close).macd()

    # calculate the macd signal (a 9 period ema of the macd line)
    def add_macd_signal(self):
        self.df['macd_signal'] = ta.trend.MACD(close=self.close).macd_signal()

    # caluclates stochastic line (%k)
    def add_stochastic_line(self):
        stoch = ta.momentum.StochasticOscillator(high=self.high, low=self.low, close=self.close)
        self.df['stoch_line'] = stoch.stoch()

    # calculate stochastic signal line (%d)
    def add_stochastic_signal_line(self):
        stoch_signal = ta.momentum.StochasticOscillator(high=self.high, low=self.low, close=self.close)
        self.df['stoch_signal'] = stoch_signal.stoch_signal()

    def determine_signal(self, dframe):
        m_line = dframe['macd_line']
        m_signal = dframe['macd_signal']
        k_line = dframe['stoch_line']
        d_signal = dframe['stoch_signal']

        action = 0

        # SELL CRITERIA: stoch %k and %d lines crossover that are >80 shortly before MACD signal and line crossover that are >0
        if (k_line.iloc[-3] > 80 and d_signal.iloc[-3] > 80 and k_line.iloc[-2] > 80 and d_signal.iloc[
            -2] > 80) and \
                ((k_line.iloc[-3] < d_signal.iloc[-3] and k_line.iloc[-2] > d_signal.iloc[-2])) and \
                (m_line.iloc[-2] > 0 and m_signal.iloc[-2] > 0 and m_line.iloc[-1] > 0 and m_signal.iloc[
                    -1] > 0) and \
                (m_line.iloc[-2] > m_signal.iloc[-2] and m_line.iloc[-1] < m_signal.iloc[-1]):

            action = -1
        # BUY CRITERIA: stoch %k and %d lines crossover that are <20 shortly before MACD signal and line crossover that are <0
        elif (k_line.iloc[-3] < 20 and d_signal.iloc[-3] < 20 and k_line.iloc[-2] < 20 and d_signal.iloc[
            -2] < 20) and \
                ((k_line.iloc[-3] > d_signal.iloc[-3] and k_line.iloc[-2] < d_signal.iloc[-2])) and \
                (m_line.iloc[-2] < 0 and m_signal.iloc[-2] < 0 and m_line.iloc[-1] < 0 and m_signal.iloc[
                    -1] < 0) and \
                (m_line.iloc[-2] < m_signal.iloc[-2] and m_line.iloc[-1] > m_signal.iloc[-1]):

            action = 1

        return (action, k_line.iloc[-2] - d_signal.iloc[-2],)

    def run_macd_stochastic_crossover(self):
        self.add_macd_line()
        self.add_macd_signal()
        self.add_stochastic_line()
        self.add_stochastic_signal_line()
        return self.determine_signal(self.df), self.df

    ''' The following methods are for plotting '''
    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 37

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-37:])[0]
        plot_df.loc[plot_df.index[-1], 'signal'] = action

    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)
        self.find_all_signals(plot_df)

        plot_df['0_line'] = 0
        plot_df['20_line'] = 20
        plot_df['80_line'] = 80

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(plot_df['macd_line'], panel=1, color='pink', width=0.75, ylabel='MACD line\n(pink) \nand signal\n(blue)')
        visualisation.add_subplot(plot_df['macd_signal'], panel=1, color='b', width=0.75)
        visualisation.add_subplot(plot_df['0_line'], panel=1, color='k', width=0.75)
        visualisation.add_subplot(plot_df['stoch_line'], panel=2, color='orange', width=0.75, ylabel=' Stochastic\n line \n(orange) \nand signal \n(green)')
        visualisation.add_subplot(plot_df['stoch_signal'], panel=2, color='forestgreen', width=0.75)
        visualisation.add_subplot(plot_df['20_line'], panel=2, color='k', width=0.75)
        visualisation.add_subplot(plot_df['80_line'], panel=2, color='k', width=0.75)

        # create final plot with title
        visualisation.plot_graph("Stochastic MACD Crossover Strategy")

