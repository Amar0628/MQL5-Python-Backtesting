from datetime import datetime
import time
import os
import copy, sys
import pandas as pd
import numpy as np
import talib
import json
from output import output

class actionWriter():
    def __init__(self, trading_algrithm):
        self.trading_algrithm = trading_algrithm

    def write_strategies(self, data):
        with open('action_test.txt', 'w') as outfile:
            json.dump(data, outfile)

    def save2csv(self,output_save, predict_result, contents, signal, prev_signal, df):
        output_save.save_csv(contents, df, signal, prev_signal, predict_result)


    
    def cleanFile(self, filename):
        del_f = open(filename, "w")
        del_f.close()
        

    def run(self):
        filename = "time_close_csv_test.csv"
        pre_Timebar = 0
        output_save = output()
        check_point = 0

        if os.path.isfile(filename) and os.stat(filename).st_size != 0:
            print("File exist and not empty")

            while True:
                if os.stat(filename).st_size != 0:
                    try:
                        with open(filename, encoding='utf-16') as f:
                            contents = f.read()
                        # you may also want to remove whitespace characters like `\n` at the end of each line
                        contents = contents.splitlines()
                        contents = [x.split('\t') for x in contents]
                        for i in range(len(contents)):
                            contents[i][0] = datetime.strptime(contents[i][0], '%Y.%m.%d %H:%M:%S')
                            contents[i][1] = float(contents[i][1]) #open
                            contents[i][2] = float(contents[i][2]) #high
                            contents[i][3] = float(contents[i][3]) #low
                            contents[i][4] = float(contents[i][4]) #close
                            contents[i][5] = int(contents[i][5]) #tick value

                        newTimebar = contents[-1][0]
                        curr_position = contents[-1][-1]
                        curr_close_price = contents[-1][4]
                        if curr_position == "Ending":
                            
                            print(">>>------------------------<<<")
                            output_save.output_csv()
                            print(">>> Server Stop <<<")
                            break
                            

                        else:
                            if pre_Timebar != newTimebar:
                                pre_Timebar = copy.deepcopy(newTimebar)
                                
                                print("Timebar: ",pre_Timebar)
                                print("curr_close_price: ",curr_close_price)
                                print("curr_position", curr_position)

                                # code from example2.py, send the data to the main_DecisionMaker.py
                                predict_result, signal, prev_signal, df  = self.trading_algrithm.predict(contents)
                                if type(predict_result) is not dict:
                                    raise ValueError("Value must return a dictionary type")
                                print("predict_result","\t",predict_result)
                                
                                # write the result to txt or csv 
                                self.write_strategies(predict_result)
                                # self.cleanFile(filename)
                                
                                self.save2csv(output_save, predict_result, contents, signal, prev_signal, df)

                                check_point += 1

                                if check_point % 50 == 0:
                                    output_save.output_csv()

                            else:
                                time.sleep(0.003)

                    except :
                        continue
                        
                else:
                    # print("File is empty")
                    time.sleep(0.001)          
        else:
            print("File not exist")