import pandas as pd
import ta
import trading_strategies.visualise as v

'''
@ Vita
https://www.dailyfx.com/forex/education/trading_tips/daily_trading_lesson/2020/01/09/macd-histogram.html

'''


class MACDCrossover:

    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))

    def add_macd_line(self):
        self.df['macd_line'] = ta.trend.MACD(close=self.df['close']).macd()

    def add_macd_signal_line(self):
        self.df['macd_signal'] = ta.trend.MACD(close=self.df['close']).macd_signal()

    def determine_signal(self,dframe):
        # sell = -1, hold = 0, buy = 1, initialise all as hold first

        action = 0
        macd = dframe['macd_line']
        signal = dframe['macd_signal']


        # SELL CRITERIA: if MACD line has crossed signal line and are > 0
        if (macd.iloc[-1] > 0 and signal.iloc[-1] > 0 and macd.iloc[-2] > 0 and signal.iloc[-2] > 0 and macd.iloc[-3]>0 and signal.iloc[-3]>0) and \
                ((macd.iloc[-3] < signal.iloc[-3] and macd.iloc[-1] > signal.iloc[-1]) or (macd.iloc[-3] > signal.iloc[-3] and macd.iloc[-1] < signal.iloc[-1])):
            action = -1

        # BUY CRITERIA: if MACD line has crossed signal line and are < 0
        if (macd.iloc[-1] < 0 and signal.iloc[-1] < 0 and macd.iloc[-2] < 0 and signal.iloc[-2] < 0 and
            macd.iloc[-3] < 0 and signal.iloc[-3] < 0) and \
                ((macd.iloc[-3] > signal.iloc[-3] and macd.iloc[-1] < signal.iloc[-1]) or (
                        macd.iloc[-3] < signal.iloc[-3] and macd.iloc[-1] > signal.iloc[-1])):
            action = 1


        return action, macd.iloc[-1]-signal.iloc[-1]

    def run_macd_crossover(self):
        self.add_macd_line()
        self.add_macd_signal_line()
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

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(plot_df['macd_line'], panel=1, color='pink', width=0.75, ylabel='MACD line\n(pink)')
        visualisation.add_subplot(plot_df['macd_signal'], panel=1, color='b', width=0.75, ylabel='MACD signal\n(blue)')

        # create final plot with title
        visualisation.plot_graph("MACD Crossover Strategy")


