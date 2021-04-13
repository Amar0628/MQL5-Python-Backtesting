import pandas as pd

"""import strategies"""
#import
from awesome_saucer import AwesomeOscillatorSaucer
from ichimoku_cloud_psar import IchimokuCloudPsar

"""loading the data set to be used as input for the AI"""
# file path
file_path = 'FXCM_EUR_GBP_H4.csv'
data = pd.read_csv(file_path)

"""setting the vaule of a pip, usually 0.0001 but 0.01 for JPY currencies, and trade differential, the price difference
    at which the trade is to be classified as a buy sell or hold."""
pips = 0.0001
trade_differential = 10*pips

"""loading all the strategies to be used as attributes for the AI"""
# instantiating the stategies list
strategies = []

# instantiate and adding all strategies objects into strategies list
strategy_1 = AwesomeOscillatorSaucer(file_path)
strategies.append(strategy_1)
strategy_2 = IchimokuCloudPsar(file_path)
strategies.append(strategy_2)

"""determining the correct signal for use as the class in AI"""
data['correct_signal'] = 0
data.loc[data['close'].shift(-10) - data['close'] > trade_differential, 'correct_signal'] = 1
data.loc[data['close'].shift(-10) - data['close'] > -trade_differential, 'correct_signal'] = -1

"""running the 10 strategies for the action and additional info
    for running in a loop, rename the run function to just run()
    in find_all_signal() add in lines
        additional_info = self.determine_signal(curr_window)[1] 
        plot_df.loc[plot_df.index[end - 1], 'additional_info'] = additional_info
    to get additional info
    get rid off the max window if you have that in the code"""

n = 0
for strategy in strategies:
    n = n+1
    strategy.run()
    strategy.find_all_signals(strategy.df)
    data["strategy_" + str(n) + "_action"] = strategy.df['signal']
    data["strategy_" + str(n) + "_additional_info"] = strategy.df['additional_info']

"""saving to csv"""
data.to_csv('FXCM_EUR_GBP_H4_post.csv')
print("Successfully generated processed file!")