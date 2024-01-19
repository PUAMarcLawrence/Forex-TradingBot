from flask import Flask, redirect, url_for, render_template, request, session, abort
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import MetaTrader5 as mt5
import pandas as pd
from waitress import serve

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

account = {
    "login" : 0,
    "password" : " ",
    "server" : " "
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
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        if request.form["ID"] != "":
            account["login"] = int(request.form["ID"])
        account["password"] = request.form["pass"]
        account["server"] = request.form["server"]
        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize(login=account["login"],password=account["password"],server=account["server"]): # login=212636007,password='9X@buA3G',server='OctaFX-Demo'
            print("failed to connect at account #{}, error code: {}".format(account["login"], mt5.last_error()))
            return render_template("login.html",Failed="Login Failed")
        else:
            print(mt5.version())
            print(mt5.account_info()._asdict())
            session["user"] = mt5.account_info().login
            return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))

        return render_template("login.html",Failed="")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    mt5.shutdown()
    return redirect(url_for("home"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == "__main__":
    app.run(host ="0.0.0.0", port=8000,debug=True) 
    # serve(app, host ="0.0.0.0", port=8000)