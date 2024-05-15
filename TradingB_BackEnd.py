#import
import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from modules.mt5_functions import get_positions,checkActivePos,close_order,buy_order,sell_order
from modules.sqlite_functions import getCurrencies,choiceRetrieve
# from modules.findTime import *
from modules.TrendML import trends

print_status = {
    "printed_closed" : False,
    "printed_open" : False,
    "loggedIn" : False
}
currencies = getCurrencies()

# Market Check Function
def checkMarket_status():
    # server date time
    datetimeNow = datetime.now() - timedelta(hours=6)
    day_of_week = datetimeNow.weekday()
    if day_of_week > 4:
        if not print_status["printed_closed"]:
            print_status["printed_closed"] = True
            print_status["printed_open"] = False
            print('Market is CLOSED...')
        return False # ("Markets are Closed")
    else:
        if not print_status["printed_open"]:
            print_status["printed_closed"] = False
            print_status["printed_open"] = True
            print('Market is OPEN....')
        return True # ("Markets are Open")

# # Momentum trading strategy
# def momentum_trading(symbol):
#     # Fetch historical data
#     data = pd.DataFrame(get_positions(symbol,'M15',100))
#     # Calculate momentum indicator (e.g., simple moving average)
#     data['SMA_short'] = data['close'].rolling(window=10).mean()
#     data['SMA_long'] = data['close'].rolling(window=30).mean()
#     # Check for buy/sell signals
#     if data['SMA_short'].iloc[-1] > data['SMA_long'].iloc[-1]:
#         # print("Buy signal detected!")
#         return 1
#         # Implement your buy order here
#     elif data['SMA_short'].iloc[-1] < data['SMA_long'].iloc[-1]:
#         # print("Sell signal detected!")
#         return 0
#         # Implement your sell order here
#     return

def main():
    print('Bot Online')
    while True:
        # server date time
        current_time = datetime.now() - timedelta(hours=6)
        if checkMarket_status() == True:
            for symbol in currencies:
                choice = choiceRetrieve(symbol)
                if choice == 1:
                    trend = trends()
                    print(trend)
                    for symbol in currencies:
                        if not checkActivePos(symbol):
                            trendSym = trend[currencies.index(symbol)]
                            # momentum = momentum_trading(symbol)
                            if trendSym == ['Up','Up','Up'] or trendSym == ['Up','Up','Down']: # and momentum == 1:
                                print("Buying")
                                buy_order(symbol,0.01)
                            elif trendSym == ['Down','Down','Down'] or trendSym == ['Down','Down','Up']: # and momentum == 0:
                                print('Selling')
                                sell_order(symbol,0.01)
                            

if __name__ == '__main__':
    main()
