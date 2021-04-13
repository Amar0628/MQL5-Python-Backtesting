# import your trading strategy here
#from sma_ema import SimpleMAExponentialMA
from trading_strategies.sma_ema import SimpleMAExponentialMA
#from trading_strategies.adx_crossover import AdxCrossover
#from trading_strategies.aroon_adx import AroonAdx
#from trading_strategies.sma_mi import SMAMI
#from trading_strategies.stochastic_oscillator_no_exit import StochasticOscillatorNoExit
#from trading_strategies.aroon_indicator import AroonIndicator
#from trading_strategies.awesome_saucer import AwesomeOscillatorSaucer
#from trading_strategies.blade_runner import BladeRunner
#from trading_strategies.bollingerbands_rsi_2 import BollingerBandsAndRSI2
#from trading_strategies.cci_macd_psar import CciMacdPsar
#from trading_strategies.dpo_candlestick import DpoCandlestick
#from trading_strategies.elder_ray_sma import ElderRaySma
#from trading_strategies.ema_3 import ThreeEma
#from trading_strategies.ema_crossover_alternative import EMACrossover
#from trading_strategies.ema_crossover_macd import EMACrossoverMACD
#from trading_strategies.ema_crossover_rsi_alternative import EMACrossoverRSI
#from trading_strategies.ema_crossover_rsi import EMACrossoverRSI
#from trading_strategies.ema_crossover import EMACrossover
#from trading_strategies.williams_stochastic import WilliamsStochastic
#from trading_strategies.macd_crossover import MACDCrossover
#from trading_strategies.macd_rsi_sma import MacdRsiSma
#from trading_strategies.macd_stochastic_crossover import MACDStochasticCrossover
#from trading_strategies.rsi_2 import Rsi2
#from trading_strategies.rsi_80_20 import Rsi8020
#from trading_strategies.triple_bollingerbands import TripleBollingerBands
#from trading_strategies.trix_ema import TrixEma
#from trading_strategies.trix_rsi import TrixRsi
#from trading_strategies.vortex_crossover import VortexCrossover
#from trading_strategies.vortex_sma import VortexSma
#from trading_strategies.williams_r_sma import WilliamsIndicator
#from trading_strategies.williams_rsi import WilliamsRsi
#from trading_strategies.commodity_channel_index import CommodityChannelIndex
#rom trading_strategies.donchian_breakout import DonchianBreakout

# optional import, only use for demo
from datetime import datetime
#using pip install panda if missing modules pandas
import pandas as pd
# non-optional import:
from actionWriter import actionWriter

class DecisionMaker:

    def __init__(self):
        self.prev_signal = 0 # what the previous signal was was e.g. 1 for buy , -1 for sell, 0 for hold
        self.prev_traded_price = 0 # this is the previously traded price for an exisiting position (entry price)
        self.curr_stop_loss = 0 # current stop loss
        self.curr_take_profit = 0 # current take profit


    # for the last candle (data) of the given currency (symbol), provided its historical data(history) predict whether to buy or sell
    def predict(self, history):

        # convert history to pandas dataframe
        history_dataframe = pd.DataFrame(history, columns=("time", "open", "high", "low", "close", "tick_volume","pos"))

        # extract meaningful values
        prev_close_price = history[-2][4]
        curr_close_price = history[-1][4]
        curr_high_price = history[-1][2]
        curr_low_price = history[-1][3]
        date = history[-1][0]

        # adjust TP/SL values here, remember to x100 if testing on JPY currency
        #take_profit = 0.0200
        take_profit = 0.0050
        #stop_loss = -0.0250
        stop_loss = -0.0020


        print("-----")
        print("date: ", date)
        print("current price is: ", curr_close_price)

        # Run strategy here #
        strategy = SimpleMAExponentialMA(history)
        #strategy = AdxCrossover(history)
        #strategy = AroonAdx(history)
        #strategy = SMAMI(history)
        #strategy = StochasticOscillatorNoExit(history)
        #strategy = AroonIndicator(history)
        #strategy = AwesomeOscillatorSaucer(history)
        #strategy = BladeRunner(history)
        #strategy = BollingerBandsAndRSI2(history)
        #strategy = CciMacdPsar(history)
        #strategy = DpoCandlestick(history)
        #strategy = ElderRaySma(history)
        #strategy = ThreeEma(history)
        #strategy = EMACrossover(history)
        #strategy = EMACrossoverMACD(history)
        #strategy = EMACrossoverRSI(history)
        #strategy = EMACrossover(history)
        #strategy = WilliamsStochastic(history)
        #strategy = MACDCrossover(history)
        #strategy = MacdRsiSma(history)
        #strategy = MACDStochasticCrossover(history)
        #strategy = Rsi2(history)
        #strategy = Rsi8020(history)
        #strategy = TripleBollingerBands(history)
        #strategy = TrixEma(history)
        #strategy = TrixRsi(history)
        #strategy = VortexCrossover(history)
        #strategy = VortexSma(history)
        #strategy = WilliamsIndicator(history)
        #strategy = DonchianBreakout(history)
        #strategy = CommodityChannelIndex(history)

        signal_lst, df = strategy.run_sma_ema()
        #signal_lst, df = strategy.run_aroon_adx()
        #signal_lst, df = strategy.run_awesome_oscillator_saucer()
        #signal_lst, df = strategy.run_bollingerbands_rsi_2()
        #signal_lst, df = strategy.run_dpo_candlestick()
        #signal_lst, df = strategy.run_elder_ray()
        #signal_lst, df = strategy.run_ema_3()
        #signal_lst, df = strategy.run_ema_crossover()
        #signal_lst, df = strategy.run_ema_crossover_macd()
        #signal_lst, df = strategy.run_ema_crossover_rsi()
        #signal_lst, df = strategy.run_ema_crossover()
        #signal_lst, df = strategy.run_williams_stochastic()
        #signal_lst, df = strategy.run_macd_crossover()
        #signal_lst, df = strategy.run_macd_rsi_sma()
        #signal_lst, df = strategy.run_macd_stochastic_crossover()
        #signal_lst, df = strategy.run_rsi2()
        #signal_lst, df = strategy.run_triple_bollinger_bands()
        #signal_lst, df = strategy.run_trix_ema()
        #signal_lst, df = strategy.run_trix_rsi()
        #signal_lst, df = strategy.run_trix_rsi()
        #signal_lst, df = strategy.run_vortex_sma()
        #signal_lst, df = strategy.run_williams_indicator()
        #signal_lst, df = strategy.run_donchian_breakout()
        #signal_lst, df = strategy.run()
        signal = signal_lst[0]
        

        # first check if stop loss/take profit has been triggered

        if self.prev_signal == 1 and ((self.curr_take_profit != 0 and curr_high_price >= self.curr_take_profit) or (self.curr_stop_loss != 0 and curr_low_price <= self.curr_stop_loss)):
            self.prev_signal = 0 # since the sl/tp was triggered, we reset position

        if self.prev_signal == -1 and ((self.curr_take_profit != 0 and curr_low_price <= self.curr_take_profit) or (self.curr_stop_loss != 0 and curr_high_price >= self.curr_stop_loss)):
            self.prev_signal = 0 # since the sl/tp was triggered, we reset position
        
        print("signal: ",signal)
        print("prev_signal: ",self.prev_signal)
        # then we look at the signal returned
        if signal == 1:

            # if previous signal was a sell, close off the position
            if self.prev_signal == -1:
                self.prev_signal = 0 # make previous signal 0 as we don't have an active position
                return {"action":"POSITION_CLOSE_SYMBOL"} , signal, self.prev_signal, df #close

            # if previous signal was 0, there was no active position, open a long position
            if self.prev_signal == 0:
                self.prev_signal = signal
                self.prev_traded_price = curr_close_price
                self.curr_stop_loss = curr_close_price + stop_loss
                self.curr_take_profit = curr_close_price + take_profit
                return {"action":"ORDER_TYPE_BUY", #buy
                        "takeprofit": curr_close_price + take_profit,
                        "stoploss": curr_close_price + stop_loss}, signal, self.prev_signal, df

            # otherwise, the previous signal was another buy (pre_signal == 1)
            # as a result, we do not buy again, instead we adjust the SL/TP
            else:
                self.prev_signal = signal 

                #if its a higher buy signal we increase our TP/SL by the same spread as the original
                if curr_close_price > prev_close_price and curr_close_price > self.prev_traded_price:
                    self.curr_stop_loss = curr_close_price + stop_loss
                    self.curr_take_profit = curr_close_price + take_profit
                    return {"action":"POSITION_MODIFY",
                            "takeprofit": curr_close_price + take_profit,
                            "stoploss": curr_close_price + stop_loss}, signal, self.prev_signal , df

                #if its a lower buy signal we dont change our take profit or stop loss
                else:
                    return {"action":"skip"}, signal, self.prev_signal , df

        if signal == -1:

            # if previous signal was a buy, close off the position
            if self.prev_signal == 1:
                self.prev_signal = 0 # make previous signal 0 as we don't have an active position
                return {"action":"POSITION_CLOSE_SYMBOL"} , signal, self.prev_signal, df #close

            # if previous signal was 0, there was no active position, open a short position
            if self.prev_signal == 0:
                self.prev_signal = signal
                self.prev_traded_price = curr_close_price
                self.curr_stop_loss = curr_close_price - stop_loss
                self.curr_take_profit = curr_close_price - take_profit
                return {"action":"ORDER_TYPE_SELL", #sell
                        "takeprofit": curr_close_price - take_profit,
                        "stoploss": curr_close_price - stop_loss}, signal, self.prev_signal , df

            # otherwise, the previous signal was another sell
            # as a result, we do not sell again, instead we adjust the SL/TP
            else:
                #if its a lower sell signal we increase our take profit and increase our stop loss by the same spread as the original
                if curr_close_price < prev_close_price and curr_close_price < self.prev_traded_price:
                    self.curr_stop_loss = curr_close_price - stop_loss
                    self.curr_take_profit = curr_close_price - take_profit
                    return {"action":"POSITION_MODIFY",
                            "takeprofit": curr_close_price - take_profit,
                            "stoploss": curr_close_price - stop_loss}, signal, self.prev_signal , df

                #if its a lower sell signal we dont change our take profit or stop loss aka do nothing
                else:
                    return {"action":"skip"}, signal, self.prev_signal , df

        if signal == 0:
            return {"action":"skip"}, signal, self.prev_signal , df


ai = DecisionMaker()
executor = actionWriter(ai)
executor.run()
