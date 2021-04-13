import pandas as pd
import trading_strategies.visualise as v

'''
### Author: Wilson and Vita ###
Strategy from:
https://forexwithanedge.com/ema-trading-strategy/
This strategy looks for crosses in the 50 and 20 ema and places a position based on a crosses

'''

class EMACrossover:

    #constructor
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        # self.df = pd.DataFrame(inputs)

    def add_20_ema(self):
        self.df['20ema'] = self.df['close'].ewm(span=20, adjust=False).mean()

    def add_50_ema(self):
        self.df['50ema'] = self.df['close'].ewm(span=50, adjust=False).mean()

    def add_distance_between_20ema_and_50ema(self):
        self.df['distance'] = self.df['20ema'] - self.df['50ema']

    def determine_signal(self, dframe):
        action = 0
        ema_20 = dframe['20ema']
        ema_50 = dframe['50ema']
        close = dframe['close']

        # buy if 20 ema crosses above 50 ema
        if (ema_20.iloc[-1] > ema_50.iloc[-1]):
            action = 1

        # sell if 20 ema crosses below 50 ema
        if (ema_20.iloc[-1] < ema_50.iloc[-1]):
            action = -1

        return action, ema_20.iloc[-1] - close.iloc[-1]

    def run_ema_crossover(self):
        self.add_20_ema()
        self.add_50_ema()
        return self.determine_signal(self.df), self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 2

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-2:])[0]
        plot_df.loc[plot_df.index[-1], 'signal'] = action

    def plot_graph(self):
        # create shallow copy for plotting so as to not accidentally impact original df
        plot_df = self.df.copy(deep=False)

        self.find_all_signals(plot_df)

        plot_df = plot_df[100:200]

        # initialise visualisation object for plotting
        visualisation = v.Visualise(plot_df)

        # determining one buy signal example for plotting
        visualisation.determine_buy_marker()

        # determining one sell signal example for plotting
        visualisation.determine_sell_marker()

        # add subplots
        visualisation.add_subplot(plot_df['20ema'], color='violet', width=0.75)
        visualisation.add_subplot(plot_df['50ema'], color='orange', width=0.75)

        # create final plot with title
        visualisation.plot_graph("EMA Crossover Strategy Alternative")


# # strategy = EMACrossover(r"C:\Users\Wilson\Documents\INFO3600\USD_JPY_M15.csv")
# strategy = EMACrossover('/Users/vhuang/INFO3600/FXCM_EUR_USD_H4_1.csv')
# print(strategy.run_ema_crossover())
# strategy.plot_graph()

