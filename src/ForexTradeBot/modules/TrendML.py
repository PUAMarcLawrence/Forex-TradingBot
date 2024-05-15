import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from modules.mt5_functions import get_positions
from modules.sqlite_functions import getCurrencies

# Data collection
def fetch_data(symbol, timeframe,num_bars):
    rates = get_positions(symbol, timeframe, num_bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

# Preprocessing and feature extraction
def preprocess_data(df):
    # Add more preprocessing steps as needed
    df['close_shifted'] = df['close'].shift(-1)
    df['trend'] = (df['close_shifted'] > df['close']).astype(int)
    return df[['open', 'high', 'low', 'close', 'tick_volume']], df['trend']

# Train classifier
def train_classifier(X_train, y_train):
    clf = LogisticRegression(solver='lbfgs', max_iter=1000)
    X_train = pd.DataFrame(X_train)
    X_train.columns = ['open','high','low','close','tick_volume']
    clf.fit(X_train, y_train)
    return clf

# Predict trend
def predict_trend(symbol, timeframe, clf,num_bars):
    df = fetch_data(symbol, timeframe,num_bars)
    X, y = preprocess_data(df)
    prediction = clf.predict(X.tail(1))[0]
    return "Up" if prediction == 1 else "Down"

def trendMain(symbol,timeframe,num_bars):
    # Retrieve holc
    df= fetch_data(symbol,timeframe,num_bars)
    X,y = preprocess_data(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = train_classifier(X_train, y_train)

    # percent accuracy(req. from sklearn.metrics import accuracy_score)
    # y_pred = clf.predict(X_test)
    # print("Accuracy:", accuracy_score(y_test, y_pred))

    trend = predict_trend(symbol, timeframe, clf,num_bars)
    return trend

def trends():
    Alltrend = []
    symbols = getCurrencies()
    timeframes=['H1','H4','D1']
    for symbol in symbols:
        trends = []
        for timeframe in timeframes:
            if timeframe == 'H1':
                bars = 20
            elif timeframe == 'H4':
                bars = 75
            else:
                bars = 20
            trends.append(trendMain(symbol,timeframe,bars))
        Alltrend.append(trends)
    return Alltrend