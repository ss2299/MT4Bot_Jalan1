from utils.MT5Function import MT5Function
from utils.DataCollect import DataCollect
from utils.FileWrite import FileWrite
import time
import datetime
import pandas as pd
import os


def writeWords(symbol, timeframe, msg):
    # Current date for make directory
    output_save_folder_path = './log/'
    output_path = os.path.join(output_save_folder_path, time.strftime('%Y%m', time.localtime(time.time())))
    today = datetime.date.today().strftime('%y%m%d')

    if not os.path.exists(output_save_folder_path):
        os.mkdir(output_save_folder_path)
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    filename = f"./{output_path}/GL_{symbol}{timeframe}-{today}.txt"

    # If there is no file then make blank new file
    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            pass

    with open(filename, 'a+', encoding='UTF8') as file:
        file.write(msg)




def main(name):
    # Order
    symbol = 'XAUUSD'
    timeframe = 5
    volume = 0.1




    sleepDelay = 5      # Second
    MT5 = MT5Function(89470822)

    ## OBOS Status
    obos_upper_cnt = 0
    obos_lower_cnt = 0
    cnt_threshold = 7
    obos_status_trend = 0       # 1 : Up, -1 : Down   -> for 1 time order
    obos_upper_level = 0.7
    obos_lower_level = -0.7

    ## Read Json file
    dc = DataCollect(symbol=symbol, timeframe=timeframe)

    ## CCI variable
    CCI_OB_flag = False
    CCI_OS_flag = False

    ## Golden Line variable
    GL_OB_flag = False
    GL_OS_flag = False

    ## Buy, Sell Flag
    orderBuy_flag = False
    orderSell_flag = False
    closeBuy_flag = False
    closeSell_flag = False



    # Init variable
    init = True

    while True:
        try:
            # While loop delay
            time.sleep(sleepDelay)

            # OBOS Counting.
            # Because prevent value change many times in intersection.
            msg = dc.fileread()
            if msg == -1:
                continue

            close = msg['close']
            obos_upper = msg['obos_upper']
            obos_lower = msg['obos_lower']
            fl1_upper = msg['FL1_upper']
            fl1_lower = msg['FL1_lower']
            gl_upper = msg['GL_upper']
            gl_lower = msg['GL_lower']
            cci = msg['CCI']
            ccima = msg['CCIMA']

            if obos_upper > obos_lower:
                obos_upper_cnt = obos_upper_cnt + 1
                obos_lower_cnt = 0
            elif obos_lower > obos_upper:
                obos_lower_cnt = obos_lower_cnt + 1
                obos_upper_cnt = 0

            ## Current Zone Area
            zone_msg = ""
            if close >= gl_upper:
                zone_msg = "GOLD UPPER"
                zone = 2
            elif close < gl_upper and close > fl1_upper:
                zone_msg = "RED ZONE  "
                zone = 1
            elif close > gl_lower and close < fl1_lower:
                zone_msg = "BLUE ZONE "
                zone = -1
            elif close <= gl_lower:
                zone_msg = "GOLD LOWER"
                zone = -2
            else:
                zone_msg = "MIDDLE WAY"
                zone = 0



            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            text = f"[{now}] OBOS UP:{obos_upper:.2f} ({obos_upper_cnt}), OBOS LO:{obos_lower:.2f} ({obos_lower_cnt}), Zone:{zone_msg}, "



            # OB, OS Limit
            CCI_OB = 200
            CCI_OS = -200



            # Golden Line Trading
            # Definition of Golden Area Condition (Upper)
            if close >= gl_upper:
                GL_OB_flag = True
            elif GL_OB_flag and close < fl1_upper:
                GL_OB_flag = False

            # Definition of Golden Are Condition (Lower)
            if close <= gl_lower:
                GL_OS_flag = True
            elif GL_OS_flag and close > fl1_lower:
                GL_OB_flag = False

            # CCI
            ## OverBought
            if cci > CCI_OB:
                CCI_OB_flag = True

            if CCI_OB_flag:
                if cci < ccima or cci <= 100:
                    closeBuy_flag = True

                    if GL_OB_flag:
                        orderSell_flag = True




            ## OverSell
            if cci < CCI_OS:
                CCI_OS_flag = True

            if CCI_OS_flag:
                if cci > ccima or cci >= -100:
                    closeSell_flag = True

                    if GL_OS_flag:
                        orderBuy_flag = True




            text += f"CCI:{cci} ,  CCISMA:{ccima} , OB_flag:{CCI_OB_flag} , OS_flag:{CCI_OS_flag}, OBOS_Status : {obos_status_trend},  "


            # Close by CCI Condition
            if closeBuy_flag:
                if MT5.positions_total() > 0:
                    text += f"Buy ({MT5.positions_total()}) positions are closed by condition"
                    MT5.closePosition(symbol=symbol, position="buy")

                closeBuy_flag = False
                CCI_OB_flag = False


            if closeSell_flag:
                if MT5.positions_total() > 0:
                    text += f"Sell ({MT5.positions_total()}) positions are closed by condition"
                    MT5.closePosition(symbol=symbol, position="sell")

                closeSell_flag = False
                CCI_OS_flag = False


            if orderBuy_flag:
                MT5.order(symbol=symbol, buysell="buy", volume=volume, slpercent=0.002, tppercent=0.00315,
                          comment="Golden", magic=2299)
                orderBuy_flag = False

            if orderBuy_flag:
                MT5.order(symbol=symbol, buysell="sell", volume=volume, slpercent=0.002, tppercent=0.00315,
                          comment="Golden", magic=2299)
                orderBuy_flag = False




            ## Enter ORDER by OBOS
            if obos_upper_cnt >= cnt_threshold and obos_status_trend != 1 :
                obos_status_trend = 1  # 1-time enter to this if phase, prevent multiple time enter during obos cycle.
                obos_status_golden = 1  # For GoldenLine Area
                if init:
                    init = False
                    continue
                if MT5.positions_total() > 0:
                    # MT5.closeAll(symbol=symbol)
                    MT5.closePosition(symbol=symbol, position="sell")

                # Filtering small wave channel
                # if obos_lower < fl1_lower and obos_lower < obos_lower_level:
                # if zone != 0:
                MT5.order(symbol=symbol, buysell="buy", volume=volume, slpercent=0.002, tppercent=0.00315, comment="OBOS", magic=2299)
                text += "Buy Order is Completed by OBOS"
                CCI_OB_flag = False             # Filter CCI close condition when enter order.

            elif obos_lower_cnt >= cnt_threshold and obos_status_trend != -1:
                obos_status_trend = -1      # 1-time enter to this if phase, prevent multiple time enter during obos cycle.
                obos_status_golden = -1     # For GoldenLine Area

                if init:
                    init = False
                    continue
                if MT5.positions_total() > 0:
                    # MT5.closeAll(symbol=symbol)
                    MT5.closePosition(symbol=symbol, position="buy")



                # Filtering small wave channel
                # if obos_lower > fl1_upper and obos_lower > obos_upper_level:
                # if zone != 0:
                MT5.order(symbol=symbol, buysell="sell", volume=volume, slpercent=0.002, tppercent=0.00315, comment="OBOS", magic=2299)
                text += "Sell Order is Completed by OBOS"
                CCI_OS_flag = False  # Filter CCI close condition when enter order.







            # Print Message
            print(text)
            writeWords(symbol=symbol,timeframe=timeframe , msg=text + "\n")



        except Exception:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'[{now}] Exception : {Exception}')








if __name__ == '__main__':
    main('Hi MT4, im telegram bot.')