import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output,State

dash.register_page(__name__, path='/')

layout = html.Div([
    
    html.Div(
        dcc.Input(id="user", type="number", placeholder="Enter User ID", className="inputbox1", style={'margin':'60px auto auto','width':'310px','height':'50px','padding':'0 15px','margin-top':'60px','font-size':'16px','border-width':'3px','border-color':'#a0a3a2','justify-content':'center'}),style={'display':'flex','justify-content':'center'}
    ),
    html.Div(
        dcc.Input(id="passw", type="password", placeholder="Enter Password",className="inputbox2", style={'margin':'10px auto auto','width':'310px','height':'50px','padding':'0 15px','font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),style={'display':'flex','justify-content':'center'}
    ),
    html.Div(
        html.Button('Login', id='verify', n_clicks=0, style={'border-width':'3px','font-size':'20px'}),
        style={'display':'flex','justify-content':'center','padding-top':'30px'}),
        html.Div(id='output1')
])