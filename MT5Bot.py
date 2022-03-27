from utils.MT5Function import MT5Function
from utils.DataCollect import DataCollect
from EncryptedInfo import EncryptedInfo
import time
import datetime
import os
import telegram
import pyautogui


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


def SendPhoto(bot, eni, msg):
    screenimage = pyautogui.screenshot("screen.png")
    screenimage.save("screen.png")
    photo = open("screen.png", 'rb')
    bot.sendPhoto(chat_id=eni.getChannelid('20K'), photo=photo, caption=msg)




def main(name):
    # Order
    symbol = 'BTCUSD'
    timeframe = 5
    volume = 0.05




    sleepDelay = 5      # Second
    MT5 = MT5Function(89470822)

    ## OBOS Status
    obos_upper_cnt = 0
    obos_lower_cnt = 0
    cnt_threshold = 7
    obos_status = 0       # 1 : Up, -1 : Down   -> for 1 time order

    ## Read Json file
    dc = DataCollect(symbol=symbol, timeframe=timeframe)

    ## CCI variable
    CCI_upper_cnt = 0
    CCI_lower_cnt = 0
    CCI_status_order = 0        # 1 : Up, -1 : Down -> for 1 time order
    CCI_status_close = 0        # 1 : Up, -1 : Down -> for 1 time order
    CCI_OB = 100
    CCI_OS = -100

    ## Buy, Sell Flag
    orderBuy_flag = False
    orderSell_flag = False
    closeBuy_flag = False
    closeSell_flag = False


    # Telegram
    eni = EncryptedInfo()
    bot = telegram.Bot(token=eni.getToken())

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
            fl2_upper = msg['FL2_upper']
            fl2_lower = msg['FL2_lower']
            gl_upper = msg['GL_upper']
            gl_lower = msg['GL_lower']
            mid = msg['MID']
            cci = msg['CCI']
            ccima = msg['CCIMA']


            # Check OBOS up or down
            if obos_upper > obos_lower:
                obos_upper_cnt = obos_upper_cnt + 1
                obos_lower_cnt = 0

            elif obos_lower > obos_upper:
                obos_lower_cnt = obos_lower_cnt + 1
                obos_upper_cnt = 0


            # Check CCI up or down
            if cci > CCI_OB:
                CCI_upper_cnt = CCI_upper_cnt + 1
                CCI_lower_cnt = 0



            if cci < CCI_OS:
                CCI_lower_cnt = CCI_lower_cnt + 1
                CCI_upper_cnt = 0





            ## Current Zone Area
            zone_msg = ""
            if close >= gl_upper:
                zone_msg = "GOLD UPPER"
                zone = 2
            elif close < gl_upper and close > fl2_upper:
                zone_msg = "RED ZONE  "
                zone = 1
            elif close > gl_lower and close < fl2_lower:
                zone_msg = "BLUE ZONE "
                zone = -1
            elif close <= gl_lower:
                zone_msg = "GOLD LOWER"
                zone = -2
            else:
                zone_msg = "MIDDLE WAY"
                zone = 0






            # CCI Conditions
            if CCI_upper_cnt > 0:

                # Sell order at Bottom
                if zone == 1 and cci <= CCI_OB and CCI_status_order != -1:          # Red Zone
                    CCI_status_order = -1
                    orderSell_flag = True

                if zone == 2 and cci <= CCI_OB and CCI_status_order != -1:          # Golden Area Upper
                    CCI_status_order = -1
                    orderSell_flag = True

                # Buy close at Top
                if close > mid and cci <= CCI_OB and CCI_status_close != 1:        # Blue Zone
                    CCI_status_close = 1
                    closeBuy_flag = True



            elif CCI_lower_cnt > 0:

                # Buy order at Bottom
                if zone == -1 and cci >= CCI_OS and CCI_status_order != 1:          # Blue Zone
                    CCI_status_order = 1
                    orderBuy_flag = True

                if zone == -2 and cci >= CCI_OS and CCI_status_order != 1:          # Golden Area Upper
                    CCI_status_order = 1
                    orderBuy_flag = True

                # Sell close at Bottom
                if close < mid and cci >= CCI_OS and CCI_status_close != -1:        # Blue Zone
                    CCI_status_close = -1
                    closeSell_flag = True


            ## Close ORDER by OBOS
            if obos_upper_cnt >= cnt_threshold and obos_status != 1 :
                obos_status = 1  # 1-time enter to this if phase, prevent multiple time enter during obos cycle.
                CCI_status_order = 1            # Make Unable Buy Position Open at Bottom
                CCI_status_close = -1           # Make Unable Sell position close

                if init == True:
                    init = False
                    continue

                closeSell_flag = True



            elif obos_lower_cnt >= cnt_threshold and obos_status != -1:
                obos_status = -1      # 1-time enter to this if phase, prevent multiple time enter during obos cycle.
                CCI_status_order = -1           # Sell Position Open
                CCI_status_close = 1            # Buy Position Close

                if init == True:
                    init = False
                    continue

                closeBuy_flag = True


            # Logging
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            text = f"[{now}] OBOS UP:{obos_upper:.2f} ({obos_upper_cnt}), OBOS LO:{obos_lower:.2f} ({obos_lower_cnt}), Zone:{zone_msg}, MID : {mid}"

            text += f"   CCI:{cci} , CCIUP:{CCI_upper_cnt}, CCIDN: {CCI_lower_cnt} , CCI_status_order : {CCI_status_order}, CCI_status_close : {CCI_status_close}"




            # Order Buy
            if orderBuy_flag == True:
                orderBuy_flag = False

                result = MT5.order(symbol=symbol, buysell="buy", volume=volume, slpercent=0.002, tppercent=0.02,
                                   comment="Order Buy", magic=2299)
                # writeWords(symbol=symbol, timeframe=timeframe, msg=result)

                text += f"Buy Order"
                time.sleep(1)
                SendPhoto(bot, eni, "Buy Order")


            # Order Sell
            if orderSell_flag == True:
                orderSell_flag = False

                result = MT5.order(symbol=symbol, buysell="sell", volume=volume, slpercent=0.002, tppercent=0.02,
                                   comment="Order Sell", magic=2299)
                # writeWords(symbol=symbol, timeframe=timeframe, msg=result)

                text += f"Sell Order"
                time.sleep(1)
                SendPhoto(bot, eni, "Sell Order")


            # Close Buy
            if closeBuy_flag == True:
                closeBuy_flag = False

                if MT5.positions_total() > 0:
                    text += f"Buy ({MT5.positions_total()}) positions are closed by condition"
                    MT5.closePosition(symbol=symbol, position="buy")



            # Close Sell
            if closeSell_flag == True:
                closeSell_flag = False

                if MT5.positions_total() > 0:
                    text += f"Sell ({MT5.positions_total()}) positions are closed by condition"
                    MT5.closePosition(symbol=symbol, position="sell")


            # Print Message
            print(text)
            writeWords(symbol=symbol,timeframe=timeframe , msg=text + "\n")



        except Exception:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'[{now}] Exception : {Exception}')






if __name__ == '__main__':
    main('Hi MT4, im telegram bot.')