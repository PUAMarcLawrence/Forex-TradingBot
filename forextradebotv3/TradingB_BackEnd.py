#import
from datetime import datetime, timedelta, time
from modules.mt5_functions import checkActivePos,buy_order,sell_order
from modules.sqlite_functions import getCurrencies,choiceRetrieve
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

def session(symbol,current_time):
    if current_time >= time(2,0) and current_time <= time(12,0):
        if "JPY" in symbol:
            return True
    if current_time >= time(10,0) and current_time <= time(19,0):
        if "EUR" in symbol:
            return True
    if not current_time.time() <= time(15,0) and current_time.time() >= time(0,0):
        if "JPY" in symbol:
            return True
    return False

def main():
    print('Bot Online')
    oldTrend = []
    while True:
        # server date time
        current_time = (datetime.now() - timedelta(hours=6)).strftime("%H:%M:%S")
        if checkMarket_status() == True:
            for symbol in currencies:
                choice = choiceRetrieve(symbol)
                if choice == 1 and session(symbol,current_time) == True:
                    trend = trends()
                    if trend != oldTrend:
                        print(trend)
                        oldTrend = trend
                    for symbol in currencies:
                        if not checkActivePos(symbol):
                            trendSym = trend[currencies.index(symbol)]
                            if trendSym == ['Up','Up','Up'] or trendSym == ['Up','Up','Down']: 
                                print("Buying")
                                buy_order(symbol,0.01)
                            elif trendSym == ['Down','Down','Down'] or trendSym == ['Down','Down','Up']: 
                                print('Selling')
                                sell_order(symbol,0.01)
                            

if __name__ == '__main__':
    main()
