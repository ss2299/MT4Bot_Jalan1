import datetime
import os, time
import json
import MetaTrader5 as mt5
from EncryptedInfo import EncryptedInfo


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
    SLPercent = 0.002

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

        if position[0].type == 1:
            order(symbol=symbol, buysell="buy", volume=volume)
            print("Sell Position is closed")

        # Buy position
        elif position[0].type == 0:
            order(symbol=symbol, buysell="sell", volume=volume)
            print("Buy Position is closed")

    else:
        print("You don't have any positions")



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

    mt5_symbol = "BITCOIN"
    lot = 0.01

    # order(symbol=mt5_symbol, volume=lot, buysell="sell")

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




            obj_pre = obj_new

        time.sleep(delayTime)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('Hello World')