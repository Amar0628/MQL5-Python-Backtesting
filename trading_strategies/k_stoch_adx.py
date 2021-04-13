import pandas as pd
import ta
import mplfinance as mpf
import numpy as np

'''
@author: Caitlin

'''


class KeltnerStochasticAdx:

    def __init__(self, inputs):
        #self.max_window = 21  # set to 180 for better understanding of trend in graph. MIN value 99
        # self.df = pd.read_csv(file_path)[-self.max_window:]
        self.df = pd.DataFrame(inputs)
        self.high = self.df['high']
        self.close = self.df['close']
        self.low = self.df['low']

    def calculate_band_upper(self):
        band_up_ind = ta.volatility.KeltnerChannel(high=self.high, low=self.low, close=self.close, n=20)
        self.df['k_band_upper'] = band_up_ind.keltner_channel_hband()

    def calculate_band_lower(self):
        band_low_ind = ta.volatility.KeltnerChannel(high=self.high, low=self.low, close=self.close, n=20)
        self.df['k_band_lower'] = band_low_ind.keltner_channel_lband()

    def calculate_stochastic_signal_line(self):
        stoch_signal = ta.momentum.StochasticOscillator(high=self.high, low=self.low, close=self.close)
        self.df['stoch_signal'] = stoch_signal.stoch_signal()

    def calculate_adx(self):
        adx_ind = ta.trend.ADXIndicator(self.df['high'], self.df['low'], self.df['close'], n = 20)
        self.df['adx'] = adx_ind.adx()

    def determine_signal(self):

        # initialise all signals to hold: 0
        self.df['signal'] = 0

        # BUY SIGNAL: candle close is below lower keltner band, stochastic signal is <=20, psar is below the candle
        self.df.loc[((self.df['high'] < self.df['k_band_lower']) & (self.df['stoch_signal'] <= 20)
                     & (self.df['adx'] >= 20)), 'signal'] = 1

        # SELL SIGNAL: candle close above upper keltner band, stochastic signal >= 80, psar below candle
        self.df.loc[((self.df['low'] > self.df['k_band_upper']) & (self.df['stoch_signal'] >= 80)
                     & (self.df['adx'] >= 20) ), 'signal'] = -1

        # return final data point's signal
        signal_col = self.df.columns.get_loc('signal')
        return (self.df.iloc[-1, signal_col],)

    def run_keltner_stochastic_adx(self):

        self.calculate_band_lower()
        self.calculate_band_upper()
        self.calculate_stochastic_signal_line()
        self.calculate_adx()
        signal = self.determine_signal()
        return signal

    '''
    the following methods are for plotting
    '''

    def determine_buy_marker(self, plot_df):
        plot_df['buy_marker'] = np.nan
        buy_index_ls = plot_df.index[(plot_df['signal'] == 1)].tolist()
        # if buy example exists
        if buy_index_ls:
            buy_marker_index = buy_index_ls[0]

        # set marker value to lower for visual purposes
        plot_df.loc[buy_marker_index, 'buy_marker'] = plot_df.loc[buy_marker_index, 'low'] - plot_df.range * 0.06

    def determine_sell_marker(self, plot_df):

        plot_df['sell_marker'] = np.nan
        sell_index_ls = plot_df.index[(plot_df['signal'] == -1)].tolist()
        # if sell example exists
        if sell_index_ls:
            sell_marker_index = sell_index_ls[0]
        # set marker value to higher for visual purposes
        plot_df.loc[sell_marker_index, 'sell_marker'] = plot_df.loc[sell_marker_index, 'high'] + plot_df.range * 0.06

    def plot_graph(self):

        # make a copy so original is unimpacted
        plot_df = self.df.copy(deep=False)

        plot_df.range = max(plot_df['high']) - min(plot_df['low'])

        # determine buy/sell marker
        self.determine_buy_marker(plot_df)
        self.determine_sell_marker(plot_df)

        # set index to datetime
        plot_df.index = pd.to_datetime(plot_df.datetime)

        # create boundary lines
        #line_80 = self.max_window * [80]
        #line_20 = self.max_window * [20]

        # create subplots to show adx, rsi and boundary values 25, 30, 70
        apds = [
            mpf.make_addplot((plot_df['adx']), panel = 2, marker='.', type="scatter", color='m', width=0.75, ylabel='psar'),
            mpf.make_addplot(plot_df['k_band_upper'], color='c', ylabel='kband upper'),
            mpf.make_addplot(plot_df['k_band_lower'], color='c', ylabel='kband lower'),
            mpf.make_addplot(plot_df['stoch_signal'], panel=1, color='k', ylabel='stochastic \nsignal line'),
            #mpf.make_addplot(line_20, panel=1, color='b', width = 0.75, linestyle = 'solid'),
            #mpf.make_addplot(line_80, panel=1, color='b', width = 0.75, linestyle = 'solid')
        ]

        # if current subset of data has a buy/sell example, add to plot
        if not plot_df['buy_marker'].isnull().all():
            apds.append(
                mpf.make_addplot(plot_df['buy_marker'], type="scatter", marker="^", markersize=60, color="green"))
        if not plot_df['sell_marker'].isnull().all():
            apds.append(
                mpf.make_addplot(plot_df['sell_marker'], type="scatter", marker="v", markersize=60, color="red"))

        # Create colour style candlestick colours to green and red
        mc = mpf.make_marketcolors(up='g', down='r')
        # set colour and grid style
        s = mpf.make_mpf_style(marketcolors=mc)
        # view plot
        mpf.plot(plot_df, type="candle", addplot=apds, style=s, title="Keltner Stochastic Psar Strategy")


