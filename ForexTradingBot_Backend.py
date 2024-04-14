#import
import MetaTrader5 as mt5
from datetime import datetime, timedelta


print_status = {
    "printed_once" : False,
    "loggedIn" : False
}

# server date time
datetimeNow = datetime.now() - timedelta(hours=6,microseconds=10)

def main():
    while True:
        day_of_week = datetimeNow.weekday()
        if day_of_week > 4:
            if not print_status["printed_once"]:
                print("Markets are Closed")
                mt5.shutdown()
                print_status["printed_once"] = True
        else:
            mt5.initialize()


if __name__ == '__main__':
    main()
