from datetime import datetime
from dateutil.relativedelta import relativedelta
import MetaTrader5 as mt5
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt

# Set veriable dictonaries
trade = {
    "symbol" : "EURUSD",
    "timeFrame" : mt5.TIMEFRAME_H1,
    "qty" : 0.01,
    "buy_order_type" : mt5.ORDER_TYPE_BUY,
    "sell_order_type" : mt5.ORDER_TYPE_SELL,
    "stop_loss_ticks" : 50,
    "take_profit_ticks" : 150
}
print_status = {
    "printed_once" : False,
    "loggedIn" : False
}

def moving_average(symbol,timeframe,timeframeS,deviation):
    # Retrieve historical data
    historical_data = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
    
    # Convert historical data to Pandas DataFrame for easier analysis
    df = pd.DataFrame(historical_data)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    # Calculate the 20-period Simple Moving Average (SMA)
    df['EMA_20'] = df['close'].ewm(span=20,adjust=False).mean()
    df['UpperBand'] = df['EMA_20'] + deviation * df['close'].rolling(window=20).std()
    df['LowerBand'] = df['EMA_20'] - deviation * df['close'].rolling(window=20).std()
    
    # EMA Crossover Strategy (Trend Analysis)
    df['Signal'] = 0  # Initialize signal column
    # Generate buy signals
    df.loc[df['close'] > df['UpperBand'], 'Signal'] = 1
    # Generate sell signals
    df.loc[df['close'] < df['LowerBand'], 'Signal'] = -1

    # Determine the trend based on SMA
    last_close = df['close'].iloc[-1]
    last_UpperBand = df['UpperBand'].iloc[-1]
    last_LowerBand = df['LowerBand'].iloc[-1]

    if df['close'].iloc[-1] > last_UpperBand and df['close'].iloc[-2] > last_UpperBand:
        EMA_trend = "Uptrend"
    elif df['close'].iloc[-1] < last_LowerBand and df['close'].iloc[-2] < last_LowerBand:
        EMA_trend = "Downtrend"  
    else:
        EMA_trend = "Sideways"

    return(f"Current {timeframeS} EMA trend {EMA_trend}")



def main():
    while True:
        serverDt = datetime.now() - relativedelta(hours=6)
        day_of_week = serverDt.weekday()
        if day_of_week > 4:
            if not print_status["printed_once"]:
                print("Markets are Closed")
                mt5.shutdown()
                print_status["printed_once"] = True
        else:
            if not print_status["loggedIn"]:
                print("Markts are Open")
                # establish MetaTrader 5 connection to a specified trading account
                if not mt5.initialize(login=212636007,password='9X@buA3G',server='OctaFX-Demo'):
                    print("initialize() failed, error code =",mt5.last_error())
                    quit()
                print("Login Successful..")
                print_status["loggedIn"] = True
                print('Trading Bot Live....')
                print("Server Date&Time:",serverDt)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    f1 = executor.submit(moving_average,trade["symbol"],mt5.TIMEFRAME_D1,"Timeframe D1",0)
                    f2 = executor.submit(moving_average,trade["symbol"],mt5.TIMEFRAME_H4,"Timeframe H4",0.5)
                    # f3 = executor.submit(moving_average,trade["symbol"],mt5.TIMEFRAME_H1,"Timeframe H1",0.5)
                    # f4 = executor.submit(moving_average,trade["symbol"],mt5.TIMEFRAME_M30,"Timeframe M30",0.5)
                    # f5 = executor.submit(moving_average,trade["symbol"],mt5.TIMEFRAME_M15,"Timeframe M15",0.5)
                    # f6 = executor.submit(moving_average,trade["symbol"],mt5.TIMEFRAME_M5,"Timeframe M5",0.5)
                    print(f1.result())
                    print(f2.result())
                    # print(f3.result())
                    # print(f4.result())
                    # print(f5.result())
                    # print(f6.result())

if __name__ == '__main__':
    main()