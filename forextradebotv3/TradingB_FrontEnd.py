# Import Modules
import math
import pandas as pd
import plotly.graph_objects as go
from dash import Dash,html,dcc,Output,Input,State
from datetime import datetime, timedelta
from plotly import subplots
from waitress import serve
from modules.sqlite_functions import database_initialize, login_retrieve, choiceRetrieve, update_choice
from modules.mt5_functions import *
# Currency pairs
currencies = ["EURUSD", "GBPUSD", "AUDUSD","USDCHF", "USDJPY"]


# initialize app
app = Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=0.5"}], external_stylesheets=["src\assets\style.css"]) # external_stylesheets=[dbc.themes.SPACELAB,dbc.icons.BOOTSTRAP])
app.title = "FOREX Trader Bot"

# Switches Account
def login_account():
    return html.Div(
        children=[
            # Summary
            html.Div(
                id="login-summary",
                className="row summary",
                n_clicks=0,
                children=[
                    html.P("ACCOUNT: " + str(accountInfo('login')))
                ],
            ),
            # Contents
            html.Div(
                id="login-contents",
                className="row details",
                children=[
                    # Button for login
                    html.Div(
                        className="button-login",
                        children=[
                            html.Div(
                                children=[
                                    "ID: ",
                                    dcc.Input(
                                        id='user-login',
                                        type='number'),
                                ],style={"padding-left": "45px"}
                            ),
                            html.Div(
                                children=[
                                    "Password: ",
                                    dcc.Input(
                                        id='pass-login',
                                        type='password'),
                                ]
                            ),
                            html.Div(
                                children=[
                                    "Server: ",
                                    dcc.Dropdown(
                                        ['OctaFX-Demo','OctaFX-Real2','OctaFX-Real'],
                                        'OctaFX-Demo',
                                        id= 'FX-Server'
                                    )
                                ]
                            ),
                            html.Button(
                                id="Login-user",
                                children="login",
                                n_clicks=0,
                            ),
                            html.Div(id = 'login-msg')
                        ]
                    ),
                ],
            ),
        ]
    )

# Creates HTML Bid and Ask (Buy/Sell buttons)
def get_row(currency_pair):
    data = getSymbolTick(currency_pair)
    return html.Div(
        children=[
            # Summary
            html.Div(
                id=currency_pair + "summary",
                className="row summary",
                n_clicks=0,
                children=[
                    html.Div(
                        id=currency_pair + "row",
                        className="row",
                        children=[
                            html.P(
                                currency_pair,  # currency pair name
                                id=currency_pair,
                                className="three-col",
                            ),
                            html.P(
                                data['bid'],  # Bid value
                                id=currency_pair + "bid",
                                className="three-col",
                            ),
                            html.P(
                                data['ask'],  # Ask value
                                id=currency_pair+ "ask",
                                className="three-col",
                            ),
                            html.Div(
                                data['time'],
                                id=currency_pair
                                + "index",  # we save index of row in hidden div
                                style={"display": "none"},
                            ),
                        ],
                    )
                ],
            ),
            # Contents
            html.Div(
                id=currency_pair + "contents",
                className="row details",
                children=[
                    # Button for bot
                    html.Div(
                        className="button-buy-sell-chart",
                        children=[
                            html.Button(
                                id=currency_pair + "Bot",
                                children="Bot",
                                n_clicks=0,
                            )
                        ],
                    ),
                    # Button to display currency pair chart
                    html.Div(
                        className="button-buy-sell-chart-right",
                        children=[
                            html.Button(
                                id=currency_pair + "Button_chart",
                                children="Chart",
                                n_clicks=1
                                if currency_pair in ["EURUSD", "USDCHF"]
                                else 0,
                            )
                        ],
                    ),
                ],
            ),
        ]
    )

# color of Bid & Ask rates
def get_color(a, b):
    if a == b:
        return "white"
    elif a > b:
        return "#45df7e"
    else:
        return "#da5657"

# Replace ask_bid row for currency pair with colored values
def replace_row(currency_pair, index, bid, ask):
    data = getSymbolTick(currency_pair)
    return [
        html.P(
            currency_pair, id=currency_pair, className="three-col"  # currency pair name
        ),
        html.P(
            round(data['bid'],4),  # Bid value
            id=currency_pair + "bid",
            className="three-col",
            style={"color": get_color(data['bid'], bid)},
        ),
        html.P(
            round(data['ask'],4),  # Ask value
            className="three-col",
            id=currency_pair + "ask",
            style={"color": get_color(data['ask'], ask)},
        ),
        html.Div(
            data["time"], id=currency_pair + "index", style={"display": "none"}
        ),  # save index in hidden div
    ]

# Display big numbers in readable format
def human_format(num):
    try:
        num = float(num)
        # If value is 0
        if num == 0:
            return 0
        # Else value is a number
        if num < 1000000:
            return num
        magnitude = int(math.log(num, 1000))
        mantissa = str(int(num / (1000 ** magnitude)))
        return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]
    except:
        return num

# Returns Top cell bar for header area
def get_top_bar_cell(cellTitle, cellValue):
    return html.Div(
        className="two-col",
        children=[
            html.P(className="p-top-bar", children=cellTitle),
            html.P(id=cellTitle, className="display-none", children=cellValue),
            html.P(children=human_format(cellValue)),
        ],
    )

# Returns HTML Top Bar for app layout
def get_top_bar(
        balance=accountInfo('balance'),
        equity=accountInfo('equity'),
        margin=accountInfo('margin'),
        free_margin=accountInfo('margin_free'),
        margin_level=accountInfo('margin_level'),
        open_pl=0
    ):
    return [
        get_top_bar_cell("Balance", balance),
        get_top_bar_cell("Equity",equity),
        get_top_bar_cell("Margin", margin),
        get_top_bar_cell("Free Margin", free_margin),
        get_top_bar_cell("Margin Level", margin_level),
        get_top_bar_cell("Open P/L", open_pl),
    ]

####### STUDIES TRACES ######
# Moving average
def moving_average_trace(df, fig):
    df2 = df.rolling(window=5).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="MA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig

# Exponential moving average
def e_moving_average_trace(df, fig):
    df2 = df.rolling(window=20).mean()
    trace = go.Scatter(
        x=df2.index, y=df2["close"], mode="lines", showlegend=False, name="EMA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig

# Bollinger Bands
def bollinger_trace(df, fig, window_size=10, num_of_std=5):
    price = df["close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    trace = go.Scatter(
        x=df.index, y=upper_band, mode="lines", showlegend=False, name="BB_upper"
    )

    trace2 = go.Scatter(
        x=df.index, y=rolling_mean, mode="lines", showlegend=False, name="BB_mean"
    )

    trace3 = go.Scatter(
        x=df.index, y=lower_band, mode="lines", showlegend=False, name="BB_lower"
    )

    fig.append_trace(trace, 1, 1)  # plot in first row
    fig.append_trace(trace2, 1, 1)  # plot in first row
    fig.append_trace(trace3, 1, 1)  # plot in first row
    return fig

# Accumulation Distribution
def accumulation_trace(df):
    df["volume"] = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (
        df["high"] - df["low"]
    )
    trace = go.Scatter(
        x=df.index, y=df["volume"], mode="lines", showlegend=False, name="Accumulation"
    )
    return trace

# Commodity Channel Index
def cci_trace(df, ndays=5):
    TP = (df["high"] + df["low"] + df["close"]) / 3
    CCI = pd.Series(
        (TP - TP.rolling(window=10, center=False).mean())
        / (0.015 * TP.rolling(window=10, center=False).std()),
        name="cci",
    )
    trace = go.Scatter(x=df.index, y=CCI, mode="lines", showlegend=False, name="CCI")
    return trace

# Price Rate of Change
def roc_trace(df, ndays=5):
    N = df["close"].diff(ndays)
    D = df["close"].shift(ndays)
    ROC = pd.Series(N / D, name="roc")
    trace = go.Scatter(x=df.index, y=ROC, mode="lines", showlegend=False, name="ROC")
    return trace

# Stochastic oscillator %K
def stoc_trace(df):
    SOk = pd.Series((df["close"] - df["low"]) / (df["high"] - df["low"]), name="SO%k")
    trace = go.Scatter(x=df.index, y=SOk, mode="lines", showlegend=False, name="SO%k")
    return trace

# Momentum
def mom_trace(df, n=5):
    M = pd.Series(df["close"].diff(n), name="Momentum_" + str(n))
    trace = go.Scatter(x=df.index, y=M, mode="lines", showlegend=False, name="MOM")
    return trace

# Pivot points
def pp_trace(df, fig):
    PP = pd.Series((df["high"] + df["low"] + df["close"]) / 3)
    R1 = pd.Series(2 * PP - df["low"])
    S1 = pd.Series(2 * PP - df["high"])
    R2 = pd.Series(PP + df["high"] - df["low"])
    S2 = pd.Series(PP - df["high"] + df["low"])
    R3 = pd.Series(df["high"] + 2 * (PP - df["low"]))
    S3 = pd.Series(df["low"] - 2 * (df["high"] - PP))
    trace = go.Scatter(x=df.index, y=PP, mode="lines", showlegend=False, name="PP")
    trace1 = go.Scatter(x=df.index, y=R1, mode="lines", showlegend=False, name="R1")
    trace2 = go.Scatter(x=df.index, y=S1, mode="lines", showlegend=False, name="S1")
    trace3 = go.Scatter(x=df.index, y=R2, mode="lines", showlegend=False, name="R2")
    trace4 = go.Scatter(x=df.index, y=S2, mode="lines", showlegend=False, name="S2")
    trace5 = go.Scatter(x=df.index, y=R3, mode="lines", showlegend=False, name="R3")
    trace6 = go.Scatter(x=df.index, y=S3, mode="lines", showlegend=False, name="S3")
    fig.append_trace(trace, 1, 1)
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 1)
    fig.append_trace(trace3, 1, 1)
    fig.append_trace(trace4, 1, 1)
    fig.append_trace(trace5, 1, 1)
    fig.append_trace(trace6, 1, 1)
    return fig

# MAIN CHART TRACES (STYLE tab)
def line_trace(df):
    trace = go.Scatter(
        x=df.index, 
        y=df["close"], 
        mode="lines", 
        showlegend=False, 
        name="line"
    )
    return trace


def area_trace(df):
    trace = go.Scatter(
        x=df.index,
        y=df["close"], 
        showlegend=False, 
        fill="toself", 
        name="area"
    )
    return trace


def bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="#888888")),
        decreasing=dict(line=dict(color="#888888")),
        showlegend=False,
        name="bar",
    )


def colored_bar_trace(df):
    return go.Ohlc(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        showlegend=False,
        name="colored bar",
    )


def candlestick_trace(df):
    return go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="#87CEEB")),
        decreasing=dict(line=dict(color="#FF0000")),
        showlegend=False,
        name="candlestick",
    )

# Returns graph figure
def get_fig(currency_pair, ask, bid, type_trace, studies, period):
    # Get OHLC data
    if period == "H1":
        bars = 115
    elif period == "H4":
        bars = 72
    else:
        bars = 48
    df = pd.DataFrame(get_positions(currency_pair,period,bars))
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace = True)
    subplot_traces = [  # first row traces
        "accumulation_trace",
        "cci_trace",
        "roc_trace",
        "stoc_trace",
        "mom_trace",
    ]
    selected_subplots_studies = []
    selected_first_row_studies = []
    row = 1  # number of subplots

    if studies:
        for study in studies:
            if study in subplot_traces:
                row += 1  # increment number of rows only if the study needs a subplot
                selected_subplots_studies.append(study)
            else:
                selected_first_row_studies.append(study)

    fig = subplots.make_subplots(
        rows=row,
        shared_xaxes=True,
        shared_yaxes=True,
        cols=1,
        print_grid=False,
        vertical_spacing=0.12,
    )

    # Add main trace (style) to figure
    fig.append_trace(eval(type_trace)(df), 1, 1)

    # Add trace(s) on fig's first row
    for study in selected_first_row_studies:
        fig = eval(study)(df, fig)

    row = 1
    # Plot trace on new row
    for study in selected_subplots_studies:
        row += 1
        fig.append_trace(eval(study)(df), row, 1)

    fig["layout"][
        "uirevision"
    ] = "The User is always right"  # Ensures zoom on graph is the same on update
    fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 400
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
    fig["layout"]["xaxis"]["tickformat"] = "%d %B <br> %Y <br> %H:%M"
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")
    fig.update_xaxes(rangebreaks=[dict(bounds=['sat', 'mon'])])

    return fig

# returns chart div
def chart_div(pair):
    return html.Div(
        id=pair + "graph_div",
        className="display-none",
        children=[
            # Menu for Currency Graph
            html.Div(
                id=pair + "menu",
                className="not_visible",
                children=[
                    # stores current menu tab
                    html.Div(
                        id=pair + "menu_tab",
                        children=["Studies"],
                        style={"display": "none"},
                    ),
                    html.Span(
                        "Style",
                        id=pair + "style_header",
                        className="span-menu",
                        n_clicks_timestamp=2,
                    ),
                    html.Span(
                        "Studies",
                        id=pair + "studies_header",
                        className="span-menu",
                        n_clicks_timestamp=1,
                    ),
                    # Studies Checklist
                    html.Div(
                        id=pair + "studies_tab",
                        children=[
                            dcc.Checklist(
                                id=pair + "studies",
                                options=[
                                    {
                                        "label": "Accumulation/D",
                                        "value": "accumulation_trace",
                                    },
                                    {
                                        "label": "Bollinger bands",
                                        "value": "bollinger_trace",
                                    },
                                    {"label": "MA", "value": "moving_average_trace"},
                                    {"label": "EMA", "value": "e_moving_average_trace"},
                                    {"label": "CCI", "value": "cci_trace"},
                                    {"label": "ROC", "value": "roc_trace"},
                                    {"label": "Pivot points", "value": "pp_trace"},
                                    {
                                        "label": "Stochastic oscillator",
                                        "value": "stoc_trace",
                                    },
                                    {
                                        "label": "Momentum indicator",
                                        "value": "mom_trace",
                                    },
                                ],
                                value=[],
                            )
                        ],
                        style={"display": "none"},
                    ),
                    # Styles checklist
                    html.Div(
                        id=pair + "style_tab",
                        children=[
                            dcc.RadioItems(
                                id=pair + "chart_type",
                                options=[
                                    {
                                        "label": "candlestick",
                                        "value": "candlestick_trace",
                                    },
                                    {"label": "line", "value": "line_trace"},
                                    {"label": "mountain", "value": "area_trace"},
                                    {"label": "bar", "value": "bar_trace"},
                                    {
                                        "label": "colored bar",
                                        "value": "colored_bar_trace",
                                    },
                                ],
                                value="candlestick_trace",
                            )
                        ],
                    ),
                ],
            ),
            # Chart Top Bar
            html.Div(
                className="row chart-top-bar",
                children=[
                    html.Span(
                        id=pair + "menu_button",
                        className="inline-block chart-title",
                        children=f"{pair} ☰",
                        n_clicks=0,
                    ),
                    # Dropdown and close button float right
                    html.Div(
                        className="graph-top-right inline-block",
                        children=[
                            html.Div(
                                className="inline-block",
                                children=[
                                    dcc.Dropdown(
                                        className="dropdown-period",
                                        id=pair + "dropdown_period",
                                        options=[
                                            {"label": "H1", "value": "H1"},
                                            {"label": "H4", "value": "H4"},
                                            {"label": "D4", "value": "D4"},
                                        ],
                                        value="H1",
                                        clearable=False,
                                    )
                                ],
                            ),
                            html.Span(
                                id=pair + "close",
                                className="chart-close inline-block float-right",
                                children="×",
                                n_clicks=0,
                            ),
                        ],
                    ),
                ],
            ),
            # Graph div
            html.Div(
                dcc.Graph(
                    id=pair + "chart",
                    className="chart-graph",
                    config={"displayModeBar": False, "scrollZoom": True},
                )
            ),
        ],
    )

def load_orders():
    orders = []
    dfPositions = getActivePos()
    for order in dfPositions:
        if order[5] > 0:
            typeO = 'Sell'
        else:
            typeO = 'Buy'
        order = {
            'Ticket': str(order[0]),
            'Time' : str(datetime.fromtimestamp(order[1])),
            'Volume': str(order[9]),
            'Symbol': str(order[16]),
            'Type': typeO,
            'TP': str(order[12]),
            'SL': str(order[11]),
            'Swap': str(order[14]),
            'Price': str(order[10]),
            'Profit': str(order[15]),
            'Status': 'open'
        }
        orders.append(order)
    dfOrders = getHistoricPos(datetime.now() - timedelta(days=30),datetime.now())
    for order in dfOrders:
        if order[13] != 0:
            if order[4] > 0:
                typeO = 'Sell'
            else:
                typeO = 'Buy'
            order = {
                'Ticket': order[1],
                'Time' : str(datetime.fromtimestamp(order[2])),
                'Volume': order[9],
                'Symbol': order[15],
                'Type': typeO,
                'TP': "NA",
                'SL': "NA",
                'Swap': order[12],
                'Price': order[10],
                'Profit': order[13],
                'Status': 'closed'
            }
            orders.append(order)
    return orders

# Dash App Layout
app.layout = html.Div(
    className="row",
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),
        # Interval component for ask bid updates
        dcc.Interval(id="i_bis", interval=1 * 1000, n_intervals=0),
        # Interval component for graph updates
        dcc.Interval(id="i_tris", interval=1 * 2000, n_intervals=0),
        # Left Panel Div
        html.Div(
            className="three columns div-left-panel",
            children=[
                # Div for Left Panel App Info
                html.Div(
                    className="div-info",
                    children=[
                        html.H5("FOREX TRADING BOT"),
                    ],
                ),
                html.Div(
                    id="login",
                    className="div-login",
                    children=[
                        login_account(),
                    ]
                ),
                # Ask Bid Currency Div
                html.Div(
                    className="div-currency-toggles",
                    children=[
                        html.P(
                            id="live_clock",
                            className="three-col",
                            children=datetime.now().strftime("%H:%M:%S"),
                        ),
                        html.P(className="three-col", children="Bid"),
                        html.P(className="three-col", children="Ask"),
                        html.Div(
                            id="pairs",
                            className="div-bid-ask",
                            children=[
                                get_row(pair) for pair in currencies
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # Right Panel Div
        html.Div(
            className="nine columns div-right-panel",
            children=[
                # Top Bar Div - Displays Balance, Equity, ... , Open P/L
                html.Div(
                    id="top_bar", 
                    className="row div-top-bar", 
                    children=get_top_bar()
                ),
                # Charts Div
                html.Div(
                    id="charts",
                    className="row",
                    children=[chart_div(pair) for pair in currencies],
                ),
                # Panel for orders
                html.Div(
                    id="bottom_panel",
                    className="row div-bottom-panel",
                    children=[
                        html.Div(
                            className="display-inlineblock",
                            children=[
                                dcc.Dropdown(
                                    id="dropdown_positions",
                                    className="bottom-dropdown",
                                    options=[
                                        {"label": "Open Positions", "value": "open"},
                                        {
                                            "label": "Closed Positions",
                                            "value": "closed",
                                        },
                                    ],
                                    value="open",
                                    clearable=False,
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        html.Div(
                            className="display-inlineblock float-right",
                            children=[
                                dcc.Dropdown(
                                    id="closable_orders",
                                    className="bottom-dropdown",
                                    placeholder="Close order",
                                )
                            ],
                        ),
                        html.Div(
                            id="orders_table", 
                            className="row table-orders"
                        ),
                    ],
                ),
            ],
        ),
        # Hidden div that stores all clicked charts (EURUSD, USDCHF, etc.)
        html.Div(id="charts_clicked", style={"display": "none"}),
        # Hidden div for each pair that stores orders
        html.Div(
            children=[
                html.Div(id=pair + "orders", style={"display": "none"})
                for pair in currencies
            ]
        ),
        # Hidden Div that stores all orders
        html.Div(
            id="orders", 
            style={"display": "none"}
        ),
    ],
)

# Dynamic Callbacks

# Replace currency pair row
def generate_ask_bid_row_callback(pair):
    def output_callback(n, i, bid, ask):
        return replace_row(pair, int(i), float(bid), float(ask))

    return output_callback

# returns string containing clicked charts
def generate_chart_button_callback():
    def chart_button_callback(*args):
        pairs = ""
        for i in range(len(currencies)):
            if args[i] > 0:
                pair = currencies[i]
                if pairs:
                    pairs = pairs + "," + pair
                else:
                    pairs = pair
        return pairs

    return chart_button_callback

# Function to update Graph Figure
def generate_figure_callback(pair):
    def chart_fig_callback(n_i, p, t, s, pairs, a, b, old_fig):

        if pairs is None:
            return {"layout": {}, "data": {}}

        pairs = pairs.split(",")
        if pair not in pairs:
            return {"layout": {}, "data": []}

        if old_fig is None or old_fig == {"layout": {}, "data": {}}:
            return get_fig(pair, a, b, t, s, p)

        fig = get_fig(pair, a, b, t, s, p)
        return fig

    return chart_fig_callback

# Function to close currency pair graph
def generate_close_graph_callback():
    def close_callback(n, n2):
        if n == 0:
            if n2 == 1:
                return 1
            return 0
        return 0

    return close_callback

#Function to update choice Database
def update_Choice_database(pair):
    def updateChoice(n_click):
        if n_click != 0:
            choice = choiceRetrieve(pair)
            if choice == 1:
                choice = 0
            else:
                choice = 1
            update_choice(pair,choice)
        choice = choiceRetrieve(pair)
        if choice == 0: return {'background-color': 'transparent'}
        if choice == 1: return {'background-color': 'green'}
    return updateChoice

# Function to open or close STYLE or STUDIES menu
def generate_open_close_menu_callback():
    def open_close_menu(n, className):
        if n == 0:
            return "not_visible"
        if className == "visible":
            return "not_visible"
        else:
            return "visible"

    return open_close_menu

# Function for hidden div that stores the last clicked menu tab
# Also updates style and studies menu headers
def generate_active_menu_tab_callback():
    def update_current_tab_name(n_style, n_studies):
        if n_style >= n_studies:
            return "Style", "span-menu selected", "span-menu"
        return "Studies", "span-menu", "span-menu selected"

    return update_current_tab_name

# Function show or hide studies menu for chart
def generate_studies_content_tab_callback():
    def studies_tab(current_tab):
        if current_tab == "Studies":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return studies_tab

# Function show or hide style menu for chart
def generate_style_content_tab_callback():
    def style_tab(current_tab):
        if current_tab == "Style":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return style_tab

# Resize pair div according to the number of charts displayed
def generate_show_hide_graph_div_callback(pair):
    def show_graph_div_callback(charts_clicked):
        if pair not in charts_clicked:
            return "display-none"
        charts_clicked="EURUSD,JPYUSD"
        charts_clicked = charts_clicked.split(",")  # [:4] max of 4 graph
        len_list = len(charts_clicked)
        classes = "chart-style"
        if len_list % 2 == 0:
            classes = classes + " six columns"
        elif len_list == 3:
            classes = classes + " four columns"
        else:
            classes = classes + " twelve columns"
        return classes

    return show_graph_div_callback

# Generate login, bot and Chart Buttons for Left Panel
def generate_contents_for_left_panel():
    def show_contents(n_clicks):
        if n_clicks is None:
            return "display-none", "row summary"
        elif n_clicks % 2 == 0:
            return "display-none", "row summary"
        return "row details", "row summary-open"

    return show_contents

def generate_login_order():
    def switch_users(n_clicks,user,password,server):
        if n_clicks % 2 == 1:
            if user is None:
                return html.P("Please Enter a Valid ID")
            elif password is None:
                return html.P("Please Enter the password")
            else:
                if not newUser(str(user),password,server):
                    return html.P("Login Failed")
            return html.P("Logged In")
    return switch_users

# Login/Switch users Callback
app.callback(
    Output('login-msg','children'),
    [Input("Login-user","n_clicks"),
     State("user-login","value"),State("pass-login","value"),State("FX-Server","value")]
    )(generate_login_order())

def update_name():
    def updateAccountName(n_clicks):
        return html.P("ACCOUNT: " + str(accountInfo('login')))
    return updateAccountName

app.callback(
    Output('login-summary','children'),
    Input("Login-user","n_clicks")
    )(update_name())

# Callback for login Button for Left Panel
app.callback(
    [Output("login-contents", "className"), Output("login-summary", "className")],
    [Input("login-summary", "n_clicks")],
    )(generate_contents_for_left_panel())

for pair in currencies:
    # Callback for Bot and Chart Buttons for Left Panel
    app.callback(
        [Output(pair + "contents", "className"), Output(pair + "summary", "className")],
        [Input(pair + "summary", "n_clicks")],
    )(generate_contents_for_left_panel())

    # Callback for className of div for graphs
    app.callback(
        Output(pair + "graph_div", "className"), [Input("charts_clicked", "children")]
    )(generate_show_hide_graph_div_callback(pair))

    # Callback to update the actual graph
    app.callback(
        Output(pair + "chart", "figure"),
        [
            Input("i_tris", "n_intervals"),
            Input(pair + "dropdown_period", "value"),
            Input(pair + "chart_type", "value"),
            Input(pair + "studies", "value"),
            Input("charts_clicked", "children"),
        ],
        [
            State(pair + "ask", "children"),
            State(pair + "bid", "children"),
            State(pair + "chart", "figure"),
        ],
    )(generate_figure_callback(pair))

    # updates the ask and bid prices
    app.callback(
        Output(pair + "row", "children"),
        [Input("i_bis", "n_intervals")],
        [
            State(pair + "index", "children"),
            State(pair + "bid", "children"),
            State(pair + "ask", "children"),
        ],
    )(generate_ask_bid_row_callback(pair))

    # close graph by setting to 0 n_clicks property
    app.callback(
        Output(pair + "Button_chart", "n_clicks"),
        [Input(pair + "close", "n_clicks")],
        [State(pair + "Button_chart", "n_clicks")],
    )(generate_close_graph_callback())

    # updates the database of currency pair choices
    app.callback(
        Output(pair + "Bot","style"),
        Input(pair + "Bot","n_clicks")
    )(update_Choice_database(pair))

    # show or hide graph menu
    app.callback(
        Output(pair + "menu", "className"),
        [Input(pair + "menu_button", "n_clicks")],
        [State(pair + "menu", "className")],
    )(generate_open_close_menu_callback())

    # stores in hidden div name of clicked tab name
    app.callback(
        [
            Output(pair + "menu_tab", "children"),
            Output(pair + "style_header", "className"),
            Output(pair + "studies_header", "className"),
        ],
        [
            Input(pair + "style_header", "n_clicks_timestamp"),
            Input(pair + "studies_header", "n_clicks_timestamp"),
        ],
    )(generate_active_menu_tab_callback())

    # hide/show STYLE tab content if clicked or not
    app.callback(
        Output(pair + "style_tab", "style"), [Input(pair + "menu_tab", "children")]
    )(generate_style_content_tab_callback())

    # hide/show MENU tab content if clicked or not
    app.callback(
        Output(pair + "studies_tab", "style"), [Input(pair + "menu_tab", "children")]
    )(generate_studies_content_tab_callback())

# updates hidden div with all the clicked charts
app.callback(
    Output("charts_clicked", "children"),
    [Input(pair + "Button_chart", "n_clicks") for pair in currencies],
    [State("charts_clicked", "children")],
)(generate_chart_button_callback())

# updates hidden orders div with all pairs orders
@app.callback(
    Output("orders", "children"),
    Input("closable_orders", "value"),
)
# close order function
def close_orders(ticket):
    if ticket != None:
        close_order(ticket)
    return

# Callback to update Orders Table
@app.callback(
    Output("orders_table", "children"),
    [Input("interval", "n_intervals"), Input("dropdown_positions", "value")],
)
def update_order_table(n, position):
    headers = [
        'Ticket',
        'Time',
        'Volume',
        'Symbol',
        'Type',
        'TP',
        'SL',
        'Swap',
        'Price',
        'Profit',
        'Status'
    ]
    orders = load_orders()
    # If there are no orders
    if len(orders) < 1:
        return [
            html.Table(html.Tr(children=[html.Th(title) for title in headers])),
            html.Div(
                className="text-center table-orders-empty",
                children=[html.P("No " + position + " positions data row")],
            ),
        ]
    
    rows = []
    for order in load_orders():
        tr_childs = []
        for attr in order:
            if str(order["Status"]) == position:
                tr_childs.append(html.Td(order[attr]))
        # Color row based on profitability of order
        if float(order["Profit"]) >= 0:
            rows.append(html.Tr(className="profit", children=tr_childs))
        else:
            rows.append(html.Tr(className="no-profit", children=tr_childs))
    return html.Table(children=[html.Tr([html.Th(title) for title in headers])] + rows)

# Update Options in dropdown for Open and Close positions
@app.callback(Output("dropdown_positions", "options"), [Input("interval", "n_intervals")])
def update_positions_dropdown(n):
    orders = load_orders()
    closeOrders = 0
    openOrders = 0
    if orders is not None:
        for order in orders:
            if order["Status"] == "closed":
                closeOrders += 1
            if order["Status"] == "open":
                openOrders += 1
    return [
        {"label": "Open positions (" + str(openOrders) + ")", "value": "open"},
        {"label": "Closed positions (" + str(closeOrders) + ")", "value": "closed"},
    ]

# Callback to close orders from dropdown options
@app.callback(Output("closable_orders", "options"), [Input("interval", "n_intervals")])
def update_close_dropdown(n):
    orders = load_orders()
    options = []
    if orders is not None:
        for order in orders:
            if order["Status"] == "open":
                options.append({"label": order["Ticket"], "value": order["Ticket"]})
    return options

# Callback to update Top Bar values
@app.callback(Output("top_bar", "children"), [Input("interval", "n_intervals")])
def update_top_bar(n):
    balance="%.2F" % accountInfo('balance')
    equity="%.2F" % accountInfo('equity')
    margin="%.2F" % accountInfo('margin')
    free_margin="%.2F" % accountInfo('margin_free')
    margin_level="%.2F" % accountInfo('margin_level') + "%"
    positions=getActivePos()
    open_pl="%.2F" %sum(pd.DataFrame(list(positions),columns=positions[0]._asdict().keys()).profit) if len(positions) > 0 else 0
    return get_top_bar(balance, equity, margin, free_margin, margin_level, open_pl)


# Callback to update live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    datetimeNow = datetime.now() - timedelta(hours=6,microseconds=10)
    return datetimeNow.strftime("%b %d %Y %H:%M:%S")

if __name__ == '__main__':
    # app.run(host="0.0.0.0",port=8000,debug=True)
    serve(app.server, host='0.0.0.0', port=8000,threads=10)
