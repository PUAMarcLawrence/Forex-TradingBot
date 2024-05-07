import MetaTrader5 as mt5
import pandas as pd
from modules.sqlite_functions import login_retrieve, update_account

TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1']
TIMEFRAME_DICT = {
    'M1': mt5.TIMEFRAME_M1,
    'M5': mt5.TIMEFRAME_M5,
    'M15': mt5.TIMEFRAME_M15,
    'M30': mt5.TIMEFRAME_M30,
    'H1': mt5.TIMEFRAME_H1,
    'H4': mt5.TIMEFRAME_H4,
    'D1': mt5.TIMEFRAME_D1,
}

# initialize connection
def initializeMT5():
    userData,userPass,serverData = login_retrieve()
    if not mt5.initialize(login=int(userData),password=userPass, server=serverData):
        return False
    print("Login Success")
    return True

# refresh connection
def refreshInitialization():
    userData,userPass,serverData = login_retrieve()
    mt5.initialize(login=int(userData),password=userPass, server=serverData)
    return

# New user Function
def newUser(userData,userPass,serverData):
    if not mt5.initialize(login=int(userData),password=userPass, server=serverData):
        return False
    print("Login Success")
    update_account(userData,userPass,serverData)
    return True

# Parse symbol info
def getSymbolTick(symbol):
    refreshInitialization()
    return mt5.symbol_info_tick(symbol)._asdict()

# Parse Account Info
def accountInfo(info):
    refreshInitialization()
    account = mt5.account_info()
    accountDict = {
        'login' : account.login,
        'balance':account.balance,
        'equity': account.equity,
        'margin': account.margin,
        'margin_free':account.margin_free,
        'margin_level':account.margin_level,
    }
    return accountDict[info]

# Parse all active positions
def getActivePos():
    refreshInitialization()
    return mt5.positions_get()

# parse history orders
def getHistoricPos(fromData,toData):
    refreshInitialization()
    return mt5.history_deals_get(fromData,toData)

# parse for active positions by num of bars
def get_positions(symbol,timeframe,bars):
    refreshInitialization()
    rates=mt5.copy_rates_from_pos(symbol,TIMEFRAME_DICT[timeframe],0,bars)
    return rates

# check for active positions
def checkActivePos(ticker):
    refreshInitialization()
    positions = mt5.positions_get(symbol=ticker)
    df = pd.DataFrame(positions)
    if positions != ():
        return df.iloc[0,0]
    return None

# create Order
def create_order(symbol,qty,order_type,price,SL,comment):
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": qty,
        "type": order_type,
        "price": price,
        "SL": SL,
        'comment':comment,
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_FOK,
    }
    # send a trading request
    order = mt5.order_send(request)
    print(order)
    return
# buy order
def buy_order(symbol,volume):
    refreshInitialization()
    buy_price = mt5.symbol_info_tick(symbol).ask
    point = mt5.symbol_info(symbol).point
    buy_sl = buy_price - (50 * point)
    create_order(symbol,volume,mt5.ORDER_TYPE_BUY,mt5.symbol_info_tick(symbol).ask,buy_sl,'Bot Buying')
    return

# sell order
def sell_order(symbol,volume):
    refreshInitialization()
    sell_price = mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point
    sell_sl = sell_price + (50 * point)
    create_order(symbol,volume,mt5.ORDER_TYPE_BUY,mt5.symbol_info_tick(symbol).bid,sell_sl,'Bot Selling')
    return

# close Order
def close_order(ticket):
    position = mt5.positions_get(ticket=int(ticket))
    df = pd.DataFrame(position)
    if position == None:
        print("failed, error code =",mt5.last_error())
        return("No such Order!")
    if df.iloc[0,5] > 0:
        typeO = mt5.ORDER_TYPE_BUY
        priceO = mt5.symbol_info_tick(df.iloc[0,16]).bid
    else:
        typeO = mt5.ORDER_TYPE_SELL
        priceO = mt5.symbol_info_tick(df.iloc[0,16]).ask
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": df.iloc[0,16],
        "volume": df.iloc[0,9],
        "type": typeO,
        "position": int(df.iloc[0,0]),
        "price": priceO,
        "comment":'Close Position',
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    # send a trading request
    result = mt5.order_send(request)
    print(result)
    return

# get symbol names
# def get_symbol_names():
#     # get symbols
#     symbols = mt5.symbols_get()
#     symbols_df = pd.DataFrame(symbols, columns=symbols[0]._asdict().keys())
#     symbol_names = symbols_df['name'].tolist()
#     return symbol_names
