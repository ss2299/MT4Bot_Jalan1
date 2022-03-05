import os, time
import json
import MetaTrader5 as mt5
import datetime
from EncryptedInfo import EncryptedInfo

def order(symbol, volume, buysell):

    ordertype = mt5.ORDER_TYPE_BUY
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
        "sl": 0.0,
        "tp": 0.0,
        "deviation": 0,
        "magic": 23400,
        "comment": "MT5 Auto",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    order = mt5.order_send(request)
    print(order)

def closeAll(symbol):
    position = mt5.positions_get(symbol=symbol)
    volume = position[0][9]

    # Sell position
    print(position[0].type)


    if position[0].type == 1:
        print("Sell Position")
        order(symbol=symbol, buysell="buy", volume=volume)

    # Buy position
    elif position[0].type == 0:
        print("Buy Position")
        order(symbol=symbol, buysell="sell", volume=volume)


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
    lot = 1

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
                    order(symbol=mt5_symbol, volume=lot, buysell="buy")


                elif obj_new['BITCOIN']['OBOS'] == 0:
                    print("OBOS IS DOWN!")
                    closeAll(symbol=mt5_symbol)
                    time.sleep(1)
                    order(symbol=mt5_symbol, volume=lot, buysell="sell")




            obj_pre = obj_new

        time.sleep(delayTime)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('Hello World')