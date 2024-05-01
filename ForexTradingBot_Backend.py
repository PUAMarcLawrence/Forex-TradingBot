#import
import MetaTrader5 as mt5
from modules.mt5_functions import buy_order
from datetime import datetime, timedelta


print_status = {
    "printed_closed" : False,
    "printed_open" : False,
    "loggedIn" : False
}

# server date time
datetimeNow = datetime.now() - timedelta(hours=6,microseconds=10)

def checkMarket_status():
    day_of_week = datetimeNow.weekday()
    if day_of_week > 4:
        if not print_status["printed_closed"]:
            print_status["printed_closed"] = True
            print_status["printed_open"] = False
            return False # ("Markets are Closed")
    else:
        if not print_status["printed_open"]:
            print_status["printed_closed"] = False
            print_status["printed_open"] = True
            return True # ("Markets are Open")

def percent_change():
    print("percent change executed")

def main():
    while True:
        while checkMarket_status():
            percent_change()
    
if __name__ == '__main__':
    main()
