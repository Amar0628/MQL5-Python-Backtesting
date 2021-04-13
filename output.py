
import pandas as pd

class output():
    def __init__(self):
        self.date_lst = []
        self.close_lst = []
        self.signal_lst = []
        self.prev_signal_lst = []
        self.action_lst = []


    def save_csv(self, contents, dframe, signal, prev_signal, predict_result):
        date = contents[-1][0]
        close = dframe['close'].iloc[-1]
        

        self.date_lst.append(date)
        self.close_lst.append(close)
        self.signal_lst.append(signal)
        self.prev_signal_lst.append(prev_signal)
        self.action_lst.append(predict_result["action"])


    def output_csv(self):
        output_lst = [self.date_lst,  self.close_lst, self.signal_lst, self.prev_signal_lst, self.action_lst]
        df_output = pd.DataFrame(output_lst).transpose()
        df_output.columns=['date','close_price', 'signal','prev_signal','action']
        df_output.to_csv("output.csv", index=False)
