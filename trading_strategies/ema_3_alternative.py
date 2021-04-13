import pandas as pd
import trading_strategies.visualise as v
# @author: vita
class ThreeEma:

    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        # self.df = pd.DataFrame(inputs)
        self.close = self.df['close']

    def exponential_moving_average_5(self):
        self.df['5ema'] = self.df['close'].ewm(span=5, adjust=False).mean()

    def exponential_moving_average_20(self):
        self.df['20ema'] = self.df['close'].ewm(span=20, adjust=False).mean()

    def exponential_moving_average_50(self):
        self.df['50ema'] = self.df['close'].ewm(span=50, adjust=False).mean()

    def determine_signal(self, dframe):
        action = 0 #hold

        close = dframe['close']
        ema_5 = dframe['5ema']
        ema_20 = dframe['20ema']
        ema_50 = dframe['50ema']

        # SELL CRITERIA: 5ema has crossed down under 20ema such that 5ema < 20ema < 50ema and closing price < 50 ema
        if(close.iloc[-1] < ema_50.iloc[-1]) and (ema_5.iloc[-1]<ema_20.iloc[-1]<ema_50.iloc[-1]) :
            action = -1
        # BUY CRITERIA: 5ema has crossed over 20ema such that 5ema > 20ema > 50ema and closing price is > 50 ema
        elif (self.close.iloc[-1] > ema_50.iloc[-1]) and (ema_5.iloc[-1]>ema_20.iloc[-1]>ema_50.iloc[-1]):
            action = 1

        return action, ema_50.iloc[-1]-ema_20.iloc[-1],

    def run_ema_3(self):
        self.exponential_moving_average_5()
        self.exponential_moving_average_20()
        self.exponential_moving_average_50()
        signal = self.determine_signal(self.df)
        return signal, self.df


    ''' The following methods are for plotting '''
    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 3

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-3:])[0]
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
        visualisation.add_subplot(plot_df['5ema'], color='turquoise', width=0.75)
        visualisation.add_subplot(plot_df['20ema'], color='violet', width=0.75)
        visualisation.add_subplot(plot_df['50ema'], color='orange', width=0.75)

        # create final plot with title
        visualisation.plot_graph("Three EMA Strategy")

