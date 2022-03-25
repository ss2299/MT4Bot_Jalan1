import os
import json

class DataCollect:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.filename = "GL_" + str(symbol) + str(timeframe) + ".json"
        self.filepath = r"C:\Users\ss229\AppData\Roaming\MetaQuotes\Terminal\0E9DF41E457B90231E706129F0D6BB0C\MQL4\Files" + "\\" + self.filename



    def fileread(self):
        if not os.path.exists(self.filepath):
            print("File is not existed")
            msg = -1
        else:
            with open(self.filepath) as f:
                msg = json.load(f)

        return msg



