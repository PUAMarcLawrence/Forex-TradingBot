#import
import pandas as pd
from datetime import datetime, timedelta
from modules.mt5_functions import get_positions,checkActivePos,close_order,buy_order,sell_order


print_status = {
    "printed_closed" : False,
    "printed_open" : False,
    "loggedIn" : False
}
# Next minute Finder
def find_next_min(findTime):
    current_time = datetime.now() - timedelta(hours=6)
    current_hour = current_time.hour
    current_minute = current_time.minute

    # Calculate the minutes remaining until the next hour
    minutes_remaining = 60 - current_minute

    # If there are more than 15 minutes remaining in the current hour, add 15 minutes
    if minutes_remaining >= 15:
        next_minute = current_time + timedelta(minutes=findTime - current_minute % 15)
    else:
        # If there are fewer than 15 minutes remaining, find the next hour and set the minute to 0
        next_minute = current_time.replace(hour=current_hour + 1, minute=0)

    return next_minute.strftime('%H:%M:00')

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

# Momentum trading strategy
def momentum_trading(symbol):
    # Fetch historical data
    data = pd.DataFrame(get_positions(symbol,'M15',100))
    # Calculate momentum indicator (e.g., simple moving average)
    data['SMA_short'] = data['close'].rolling(window=10).mean()
    data['SMA_long'] = data['close'].rolling(window=30).mean()
    # Check for buy/sell signals
    if data['SMA_short'].iloc[-2] < data['SMA_long'].iloc[-2] and data['SMA_short'].iloc[-1] >= data['SMA_long'].iloc[-1]:
        print("Buy signal detected!")
        return 1
        # Implement your buy order here
    elif data['SMA_short'].iloc[-2] > data['SMA_long'].iloc[-2] and data['SMA_short'].iloc[-1] >= data['SMA_long'].iloc[-1]:
        print("Sell signal detected!")
        return 0
        # Implement your sell order here
    else:
        print("No trade signal detected.")
        return 3

def tradeDecision(symbol):
    decisions = []
    decisions.append(momentum_trading(symbol))
    # Determine the most common decision
    if decisions.count(0) != decisions.count(1) and decisions != []:
        decision_counts = [decisions.count(0),decisions.count(1)]
        general_decision = decision_counts.index(max(decision_counts))
    else:
        general_decision = 3 #hold
    if general_decision != 3:
        if checkActivePos(symbol) != None:
            close_order(checkActivePos(symbol))
        match general_decision:
            case 1:
                print('buying')
                buy_order(symbol,0.01)
            case 0:
                print('selling')
                sell_order(symbol,0.01)
    else:
        print('holding')
    print(symbol)
    print(general_decision)
    return

def main():
    print('Bot Online')
    currencies = ["EURUSD", "GBPUSD", "AUDUSD","USDCHF", "USDJPY"]
    timer = find_next_min(15)
    print('next check: ',timer)
    while True:
        # server date time
        datetimeNow = datetime.now() - timedelta(hours=6)
        if checkMarket_status() == True:
            if datetimeNow.strftime('%H:%M:%S') == timer:
                for symbol in currencies:
                    tradeDecision(symbol)
                timer = find_next_min(15)
                print('next check: ',timer)

if __name__ == '__main__':
    main()
