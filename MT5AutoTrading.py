import datetime
import os, time
import json
import MetaTrader5 as mt5
import pandas as pd
import schedule
from EncryptedInfo import EncryptedInfo
from ta import trend

# Flag from CCI value above or under threshold level
CCI_overbuy_M1 = False
CCI_overbuy_M5 = False
CCI_overbuy_M15 = False
CCI_overbuy_H1 = False

CCI_oversell_M1 = False
CCI_oversell_M5 = False
CCI_oversell_M15 = False
CCI_oversell_H1 = False


# Close buy position when CCI below than CCI-SMA
CCI_overbuy_M1_close = False
CCI_overbuy_M5_close = False
CCI_overbuy_M15_close = True
CCI_overbuy_H1_close = False

CCI_oversell_M1_close = False
CCI_oversell_M5_close = False
CCI_oversell_M15_close = True
CCI_oversell_H1_close = False

# Close buy position when CCI below than CCI-SMA
CCI_overbuy_M1_notice = False
CCI_overbuy_M5_notice = False
CCI_overbuy_M15_notice = True
CCI_overbuy_H1_notice = False

CCI_oversell_M1_notice = False
CCI_oversell_M5_notice = False
CCI_oversell_M15_notice = True
CCI_oversell_H1_notice = False






def getSL(symbol, buysell, percentage):
    info_tick = mt5.symbol_info_tick(symbol)
    sl = 0

    if buysell == "buy":
        sl = info_tick.bid * (1 - percentage)

    elif buysell == "sell":
        sl = info_tick.ask * (1 + percentage)

    return sl




def order(symbol, volume, buysell):

    # 0.3% from current price
    SLPercent = 0.003

    sl = getSL(symbol=symbol, buysell=buysell, percentage=SLPercent)

    if buysell == "buy":
        ordertype = mt5.ORDER_TYPE_BUY
    elif buysell == 'sell':
        ordertype = mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": ordertype,
        "price": mt5.symbol_info_tick(symbol).ask,
        "sl": sl,
        "tp": 0.0,
        "deviation": 0,
        "magic": 23400,
        "comment": f"MT5 Auto {buysell}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    order = mt5.order_send(request)
    print(order)

def closeAll(symbol):

    if mt5.positions_total() > 0:
        position = mt5.positions_get(symbol=symbol)
        volume = position[0].volume

        # Sell position
        if position[0].type == 1:
            order(symbol=symbol, buysell="buy", volume=volume)
            print("Sell Position is closed")

        # Buy position
        elif position[0].type == 0:
            order(symbol=symbol, buysell="sell", volume=volume)
            print("Buy Position is closed")

    else:
        print("You don't have any positions")

def closePosition(symbol, buysell):

    if mt5.positions_total() > 0:
        position = mt5.positions_get(symbol=symbol)
        volume = position[0].volume

        # Sell position
        if buysell == "sell":
            order(symbol=symbol, buysell="buy", volume=volume)
            print("Sell Position is closed")

        # Buy position
        elif buysell == "buy":
            order(symbol=symbol, buysell="sell", volume=volume)
            print("Buy Position is closed")

    else:
        print("You don't have any positions")

def closebyCCI(dfM1, dfM5, dfM15, dfH1):
    global CCI_overbuy_M1_close
    global CCI_overbuy_M5_close
    global CCI_overbuy_M15_close
    global CCI_overbuy_H1_close

    global CCI_oversell_M1_close
    global CCI_oversell_M5_close
    global CCI_oversell_M15_close
    global CCI_oversell_H1_close

    sizeM1 = dfM1.shape[0]
    sizeM5 = dfM5.shape[0]
    sizeM15 = dfM15.shape[0]
    sizeH1 = dfH1.shape[0]

    if CCI_overbuy_M1_close:
        if CCI_overbuy_M1:
            if dfM1['CCI'][sizeM1-1] < dfM1['CCISMA'][sizeM1-1]:
                print("[M1] Close BUY position by CCI value under CCI-SMA")

    if CCI_oversell_M1_close:
        if CCI_oversell_M1:
            if dfM1['CCI'][sizeM1-1] > dfM1['CCISMA'][sizeM1-1]:
                print("[M1] Close SELL position by CCI value over CCI-SMA")

    if CCI_overbuy_M15_close:
        if CCI_overbuy_M15:
            if dfM15['CCI'][sizeM15-1] < dfM15['CCISMA'][sizeM15-1]:
                print("[M15] Close BUY position by CCI value under CCI-SMA")
                closePosition('BITCOIN', "buy")

    if CCI_oversell_M15_close:
        if CCI_oversell_M15:
            if dfM15['CCI'][sizeM15-1] > dfM15['CCISMA'][sizeM15-1]:
                print("[M15] Close SELL position by CCI value over CCI-SMA")
                closePosition('BITCOIN', "sell")


def checkCCI(dfM1, dfM5, dfM15, dfH1):
    overbuy_level = 220
    oversell_level = -220

    global CCI_overbuy_M1
    global CCI_overbuy_M5
    global CCI_overbuy_M15
    global CCI_overbuy_H1
    global CCI_oversell_M1
    global CCI_oversell_M5
    global CCI_oversell_M15
    global CCI_oversell_H1

    sizeM1 = dfM1.shape[0]
    sizeM5 = dfM5.shape[0]
    sizeM15 = dfM15.shape[0]
    sizeH1 = dfH1.shape[0]

    # overbuy
    if not CCI_overbuy_M1 and dfM1['CCI'][sizeM1-1] >= overbuy_level:
        CCI_overbuy_M1 = True
        print('[Start] It is overbuy in M1')
    elif CCI_overbuy_M1 and dfM1['CCI'][sizeM1-1] < overbuy_level:
        CCI_overbuy_M1 = False
        print('[Finish] It is overbuy in M1')

    if not CCI_overbuy_M5 and dfM5['CCI'][sizeM5-1] >= overbuy_level:
        CCI_overbuy_M5 = True
        print('[Start] It is overbuy in M5')
    elif CCI_overbuy_M5 and dfM5['CCI'][sizeM5-1] < overbuy_level:
        CCI_overbuy_M5 = False
        print('[Finish] It is overbuy in M5')

    if not CCI_overbuy_M15 and dfM15['CCI'][sizeM15-1] >= overbuy_level:
        CCI_overbuy_M15 = True
        print('[Start] It is overbuy in M15')
    elif CCI_overbuy_M15 and dfM15['CCI'][sizeM15-1] < overbuy_level:
        CCI_overbuy_M15 = False
        print('[Finish] It is overbuy in M15')

    if not CCI_overbuy_H1 and dfH1['CCI'][sizeH1-1] >= overbuy_level:
        CCI_overbuy_H1 = True
        print('[Start] It is overbuy in H1')
    elif CCI_overbuy_H1 and dfH1['CCI'][sizeH1-1] < overbuy_level:
        CCI_overbuy_H1 = False
        print('[Finish] It is overbuy in H1')


    # oversell
    if not CCI_oversell_M1 and dfM1['CCI'][sizeM1-1] <= oversell_level:
        CCI_oversell_M1 = True
        print('[Start] It is oversell in M1')
    elif CCI_oversell_M1 and dfM1['CCI'][sizeM1-1] > oversell_level:
        CCI_oversell_M1 = False
        print('[Finish] It is oversell in M1')

    if not CCI_oversell_M5 and dfM5['CCI'][sizeM5-1] <= oversell_level:
        CCI_oversell_M5 = True
        print('[Start] It is oversell in M5')
    elif CCI_oversell_M5 and dfM5['CCI'][sizeM5-1] > oversell_level:
        CCI_oversell_M5 = False
        print('[Finish] It is oversell in M5')

    if not CCI_oversell_M15 and dfM5['CCI'][sizeM15-1] <= oversell_level:
        CCI_oversell_M15 = True
        print('[Start] It is oversell in M15')
    elif CCI_oversell_M15 and dfM15['CCI'][sizeM15-1] > oversell_level:
        CCI_oversell_M15 = False
        print('[Finish] It is oversell in M15')

    if not CCI_oversell_H1 and dfH1['CCI'][sizeH1-1] <= oversell_level:
        CCI_oversell_H1 = True
        print('[Start] It is oversell in H1')
    elif CCI_oversell_H1 and dfH1['CCI'][sizeH1-1] > oversell_level:
        CCI_oversell_H1 = False
        print('[Finish] It is oversell in H1')




def writeWords(symbol, msg):
    # Current date for make directory
    output_save_folder_path = './log/'
    output_path = os.path.join(output_save_folder_path, time.strftime('%Y%m', time.localtime(time.time())))
    today = datetime.date.today().strftime('%y%m%d')

    if not os.path.exists(output_save_folder_path):
        os.mkdir(output_save_folder_path)
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    filename = f"./{output_path}/OBOS_{symbol}-{today}.txt"

    # If there is no file then make blank new file
    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            pass

    with open(filename, 'a+', encoding='UTF8') as file:
        file.write(msg)

def getOHLC(symbol, timeframe, count):
    if timeframe == "M1":
        timeframe = mt5.TIMEFRAME_M1
    elif timeframe == "M5":
        timeframe = mt5.TIMEFRAME_M5
    elif timeframe == "M15":
        timeframe = mt5.TIMEFRAME_M15
    elif timeframe == "H1":
        timeframe = mt5.TIMEFRAME_H1
    elif timeframe == "D1":
        timeframe = mt5.TIMEFRAME_D1

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

    return rates_frame

def getCCI(df, window_cci, window_sma):
    df['CCI'] = trend.CCIIndicator(high=df['high'], low=df['low'], close=df['close'], window=window_cci).cci()
    df['CCISMA'] = trend.sma_indicator(close=df['CCI'], window=window_sma)

    return df


def main(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'{name}')  # Press Ctrl+F8 to toggle the breakpoint.

    init = True
    delayTime = 1        # second
    filename = './MT5Interface.json'

    ## Json object
    ## -1 = Default, 1 = Buy, 0 = Sell
    ## symbol for Searching in Dialog
    symbols = ["BITCOIN", "GOLD", "BRENT"]
    signals = ["OBOS", "SIGNAL"]

    obj_new = {}
    obj_pre = {}
    for symbol in symbols:
        obj_pre[symbol.upper()] = {}
        for signal in signals:
            obj_pre[symbol.upper()][signal] = -1

    ## Sync authoization info
    eni = EncryptedInfo()


    ## Metatrader 5
    login = 5436069
    password, server = eni.getMT5info(login)

    if not mt5.initialize(login=login, server=server, password=password):
        print("initialize() failed")
        mt5.shutdown()

    # OHLC DataFrame
    df_BITCOIN_M1 = pd.DataFrame()
    df_BITCOIN_M5 = pd.DataFrame()
    df_BITCOIN_M15 = pd.DataFrame()
    df_BITCOIN_H1 = pd.DataFrame()



    mt5_symbol = "BITCOIN"
    lot = 0.01
    timecounter = 1

    while True:

        with open(filename, 'r') as f:
            obj_new = json.load(f)
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{now}] {obj_new}")


        if obj_pre != obj_new:
            if init:
                obj_pre = obj_new
                print("Initialized")
                init = False
                continue

            if obj_new['BITCOIN']['OBOS'] != obj_pre['BITCOIN']['OBOS']:
                if obj_new['BITCOIN']['OBOS'] == 1:
                    print("OBOS IS UP!")
                    closeAll(symbol=mt5_symbol)
                    time.sleep(1)
                    order(symbol=mt5_symbol, buysell="buy", volume=lot)
                    writeWords(symbol=mt5_symbol, msg=f"[{now}] OBOS IS UP. \n")


                elif obj_new['BITCOIN']['OBOS'] == 0:
                    print("OBOS IS DOWN!")
                    closeAll(symbol=mt5_symbol)
                    time.sleep(1)
                    order(symbol=mt5_symbol, buysell="sell", volume=lot)
                    writeWords(symbol=mt5_symbol, msg=f"[{now}] OBOS IS DOWN. \n")

                elif obj_new['BITCOIN']['SIGNAL'] == 1:
                    print("SIGNAL IS DOWN!")
                    # position = mt5.positions_get(symbol=symbol)
                    # if position.type == 0 and position.volume > 0:      # If we have sell position
                    #     closeAll()


                elif obj_new['BITCOIN']['SIGNAL'] == 0:
                    print("SIGNAL IS DOWN!")
                    # if position.type == 1 and position.volume > 0:      # If we have buy position
                    #     closeAll()



            # Update internal variable from JSON file
            obj_pre = obj_new



        # Every 10 Sec
        if timecounter % 10 == 0:
            df_BITCOIN_M1 = getOHLC(symbol=mt5_symbol, timeframe="M1", count=30)
            df_BITCOIN_M1 = getCCI(df=df_BITCOIN_M1, window_cci=14, window_sma=4)

            df_BITCOIN_M5 = getOHLC(symbol=mt5_symbol, timeframe="M5", count=30)
            df_BITCOIN_M5 = getCCI(df=df_BITCOIN_M5, window_cci=14, window_sma=4)

            df_BITCOIN_M15 = getOHLC(symbol=mt5_symbol, timeframe="M15", count=30)
            df_BITCOIN_M15 = getCCI(df=df_BITCOIN_M15, window_cci=14, window_sma=4)

            df_BITCOIN_H1 = getOHLC(symbol=mt5_symbol, timeframe="H1", count=30)
            df_BITCOIN_H1 = getCCI(df=df_BITCOIN_H1, window_cci=14, window_sma=4)

            checkCCI(df_BITCOIN_M1, df_BITCOIN_M5, df_BITCOIN_M15, df_BITCOIN_H1)




        time.sleep(delayTime)

        # Time Counting 1sec
        timecounter += 1






# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('Hello World')