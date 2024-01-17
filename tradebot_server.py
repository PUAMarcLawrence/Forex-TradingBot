from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import MetaTrader5 as mt5
import pandas as pd
# from waitress import serve

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

# create Order
def create_order(ticker,qty,order_type,price,sl,tp):
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": ticker,
        "volume": qty,
        "type": order_type,
        "price": price,
        'sl': sl,
        'tp': tp,
        'comment':'Python Script Order',
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_FOK,
    }
    # send a trading request
    order = mt5.order_send(request)
    print(order)
    return order
# close Order
def close_order(ticker,qty,order_type,price):
    request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": ticker,
        "volume": qty,
        "type": order_type,
        "position": mt5.positions_get()[0]._asdict()['ticket'],
        "price": price,
        "comment":'Close Position',
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    # send a trading request
    order = mt5.order_send(request)
    print(order)
    return order

app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/')
def home():
    return render_template("index.html",content="Trading Bot")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        print(user)
        password = request.form["pass"]
        print(password)
        server = request.form["server"]
        print(server)
        if not print_status["loggedIn"]:
                # establish MetaTrader 5 connection to a specified trading account
                if not mt5.initialize(): # (login=212636007,password='9X@buA3G',server='OctaFX-Demo'):
                    print("initialize() failed, error code =",mt5.last_error())
                    quit()
                mt5.login(user,password,server)
                print("Login Successful..")
                print_status["loggedIn"] = True
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    mt5.shutdown()
    return redirect(url_for("login"))

if __name__ == "__main__":
    # serve(app, host ="0.0.0.0", port=8000)
    app.run(host ="0.0.0.0", port=8000,debug=True)