# Import Packages
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import math
import datetime
import pandas as pd
import plotly.graph_objects as px
import MetaTrader5 as mt5
from dash_auth import BasicAuth
from modules.sqlite_functions import login_retrieve

def authorization_function(username, password):
    userData, passData = login_retrieve()
    if userData == username and passData == password:
            return True
    else:
        return False

# initialize app
app = Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=0.5"}], external_stylesheets=["assets\style.css"]) # external_stylesheets=[dbc.themes.SPACELAB,dbc.icons.BOOTSTRAP])
app.title = "FOREX Trader Bot"
BasicAuth(app,auth_func= authorization_function)
mt5.initialize()
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
  balance=mt5.account_info().balance, equity=mt5.account_info().equity, margin=mt5.account_info().margin, fm=mt5.account_info().margin_free, m_level=mt5.account_info().margin_level, open_pl=0
):
    return [
        get_top_bar_cell("Balance", balance),
        get_top_bar_cell("Equity", equity),
        get_top_bar_cell("Margin", margin),
        get_top_bar_cell("Free Margin", fm),
        get_top_bar_cell("Margin Level", m_level),
        get_top_bar_cell("Open P/L", open_pl),
    ]


# Dash App Layout
app.layout = html.Div(
    className="row",
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),
        # Interval component for ask bid updates
        dcc.Interval(id="i_bis", interval=1 * 2000, n_intervals=0),
        # Interval component for graph updates
        dcc.Interval(id="i_tris", interval=1 * 5000, n_intervals=0),
        # Interval component for graph updates
        dcc.Interval(id="i_news", interval=1 * 60000, n_intervals=0),
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
                # Ask Bid Currency Div
                html.Div(
                    className="div-currency-toggles",
                    children=[
                        html.P(
                            id="live_clock",
                            className="three-col",
                            children=datetime.datetime.now().strftime("%H:%M:%S"),
                        ),
                        html.P(className="three-col", children="Bid"),
                        html.P(className="three-col", children="Ask"),
                #         html.Div(
                #             id="pairs",
                #             className="div-bid-ask",
                #             children=[
                #                 get_row(first_ask_bid(pair, datetime.datetime.now()))
                #                 for pair in currencies
                            # ],
                        # ),
                    ],
                ),
                # # Div for News Headlines
                # html.Div(
                #     className="div-news",
                #     children=[html.Div(id="news", children=update_news())],
                # ),
            ],
        ),
        # Right Panel Div
        html.Div(
            className="nine columns div-right-panel",
            children=[
                # Top Bar Div - Displays Balance, Equity, ... , Open P/L
                html.Div(
                    id="top_bar", className="row div-top-bar", children=get_top_bar()
                ),
    #             # Charts Div
    #             html.Div(
    #                 id="charts",
    #                 className="row",
    #                 children=[chart_div(pair) for pair in currencies],
    #             ),
    #             # Panel for orders
    #             html.Div(
    #                 id="bottom_panel",
    #                 className="row div-bottom-panel",
    #                 children=[
    #                     html.Div(
    #                         className="display-inlineblock",
    #                         children=[
    #                             dcc.Dropdown(
    #                                 id="dropdown_positions",
    #                                 className="bottom-dropdown",
    #                                 options=[
    #                                     {"label": "Open Positions", "value": "open"},
    #                                     {
    #                                         "label": "Closed Positions",
    #                                         "value": "closed",
    #                                     },
    #                                 ],
    #                                 value="open",
    #                                 clearable=False,
    #                                 style={"border": "0px solid black"},
    #                             )
    #                         ],
    #                     ),
    #                     html.Div(
    #                         className="display-inlineblock float-right",
    #                         children=[
    #                             dcc.Dropdown(
    #                                 id="closable_orders",
    #                                 className="bottom-dropdown",
    #                                 placeholder="Close order",
    #                             )
    #                         ],
    #                     ),
    #                     html.Div(id="orders_table", className="row table-orders"),
                    # ],
                # ),
            ],
        ),
    #     # Hidden div that stores all clicked charts (EURUSD, USDCHF, etc.)
    #     html.Div(id="charts_clicked", style={"display": "none"}),
    #     # Hidden div for each pair that stores orders
    #     html.Div(
    #         children=[
    #             html.Div(id=pair + "orders", style={"display": "none"})
    #             for pair in currencies
    #         ]
    #     ),
    #     html.Div([modal(pair) for pair in currencies]),
    #     # Hidden Div that stores all orders
    #     html.Div(id="orders", style={"display": "none"}),
    ],
)

# Dynamic Callbacks

# Callback to update Top Bar values
@app.callback(Output("top_bar", "children"), [Input("interval", "n_intervals")])
def update_top_bar(n):
    balance="%.2F" % mt5.account_info().balance
    equity=mt5.account_info().equity
    margin=mt5.account_info().margin
    free_margin="%.2F" % mt5.account_info().margin_free
    margin_level="%" if margin == 0 else "%2.F" % ((equity / margin) * 100) + "%"
    equity="%.2F" % mt5.account_info().equity
    margin="%.2F" % mt5.account_info().margin
    positions=mt5.positions_get()
    open_pl=sum(pd.DataFrame(list(positions),columns=positions[0]._asdict().keys()).profit) if len(positions) > 0 else 0
    return get_top_bar(balance, equity, margin, free_margin, margin_level, open_pl)


# Callback to update live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    datetimeNow = datetime.datetime.now() - datetime.timedelta(hours=6,microseconds=10)
    return datetimeNow.strftime("%b %d %Y %H:%M:%S")






# app.layout = html.Div([
#     html.H4('ForEx Trading Bot'),
#     html.Hr(),
#     dcc.Interval(id='update', interval=1*1000),
#     html.Div(id='page-content')
# ], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})

# @callback(
#     Output('page-content', 'children'),
#     Input('update', 'n_intervals')
# )

# def display_candlestick(interval):
#     df = pd.DataFrame(mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, 24*8))
#     df['time'] = pd.to_datetime(df['time'], unit='s')
#     fig = px.Figure(data=px.Candlestick(
#         x=df['time'],
#         open=df['open'],
#         high=df['high'],
#         low=df['low'],
#         close=df['close']
#     ))
#     fig.update_xaxes(rangebreaks=[dict(bounds=['sat', 'mon'])])
#     fig.update_layout(
#         xaxis_rangeslider_visible=False,
#         # shapes = [dict(x0=0, x1=1, y0='1.08', y1='1.08', xref='paper', yref='y',line_width=2,line_color='black',label_text='Sell',label_textposition='bottom left')]
#     )
#     return dcc.Graph(figure=fig, config={'displayModeBar': False})

     
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8000,debug=True)