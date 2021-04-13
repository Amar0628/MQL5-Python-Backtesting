import pandas as pd
import trading_strategies.visualise as v

# @author: vita

# This strategy uses a 5 day simple movinng average (SMA) for sell and buy signals and a
# 144 period and 169 period exponential moving average (EMA) to determine trend direction

class SimpleMAExponentialMA:
    def __init__(self, file_path):
        self.df = pd.DataFrame(file_path, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))
        self.close = self.df['close']  # retrieves the most recent closing price

    def calculate_144ema(self):
        self.df['144ema'] = self.df['close'].ewm(span=144, min_periods=144, adjust=False).mean()

    def calculate_169ema(self):
        self.df['169ema'] = self.df['close'].ewm(span=169, min_periods=169, adjust=False).mean()

    def calculate_5sma(self):
        self.df['5sma'] = self.df['close'].rolling(window=5).mean()

    def determine_signal(self, dframe):
        action = 0  # hold

        close = dframe['close']
        ema_144 = dframe['144ema']
        ema_169 = dframe['169ema']
        sma_5 = dframe['5sma']

        # SELL CRITERIA: if closing price is below SMA and 169-period EMA is above 144-period EMA
        if (close.iloc[-1] < sma_5.iloc[-1]) and (ema_169.iloc[-1] > ema_144.iloc[-1]):
            action = -1
        # BUY CRITERIA: closing price is above SMA and 144-period EMA is above 169-period EMA
        elif (close.iloc[-1] > sma_5.iloc[-1]) and (ema_144.iloc[-1] > ema_169.iloc[-1]):
            action = 1

        return action, ema_144.iloc[-1] - ema_169.iloc[-1],

    def run_sma_ema(self):
        self.calculate_144ema()
        self.calculate_169ema()
        self.calculate_5sma()
        signal = self.determine_signal(self.df)

        return signal, self.df

    ''' The following methods are for plotting '''

    def find_all_signals(self, plot_df):
        # assign initial value of hold
        plot_df['signal'] = 0

        start = -1 * len(plot_df)
        end = start + 169

        # loop through data to determine all signals
        while end < 0:
            curr_window = plot_df[start:end]
            action = self.determine_signal(curr_window)[0]
            plot_df.loc[plot_df.index[end - 1], 'signal'] = action
            end += 1
            start += 1

        action = self.determine_signal(plot_df[-169:])[0]
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
        visualisation.add_subplot(plot_df['144ema'], color='turquoise', width=0.75)
        visualisation.add_subplot(plot_df['169ema'], color='violet', width=0.75)
        visualisation.add_subplot(plot_df['5sma'], color='orange', width=0.75)

        # create final plot with title
        visualisation.plot_graph("Simple and Exponential Moving Averages Strategy")



