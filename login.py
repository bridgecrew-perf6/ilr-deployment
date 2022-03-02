
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

corporate_tax = 12.5
kpmgBlue_hash = '#00338D'
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server
##------------------------------LOGIN LAYOUT------------------------------------

index_page = html.Div(
    [
        dbc.Button("Open modal", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Login"), close_button=False),
                dbc.ModalBody(
                    html.Div([
                        html.Div(
                            dcc.Input(id="user", type="text", placeholder="Enter Username", className="inputbox1",
                                      style={'margin-left': '35%', 'width': '450px', 'height': '45px',
                                             'padding': '10px', 'margin-top': '60px',
                                             'font-size': '16px', 'border-width': '3px', 'border-color': '#a0a3a2'
                                             }),
                        ),
                        html.Div(
                            dcc.Input(id="passw", type="password", placeholder="Enter Password", className="inputbox2",
                                      style={'margin-left': '35%', 'width': '450px', 'height': '45px',
                                             'padding': '10px', 'margin-top': '10px',
                                             'font-size': '16px', 'border-width': '3px', 'border-color': '#a0a3a2',
                                             }),
                        ),
                        html.Div(
                            dbc.Button('Verify', id='verify', n_clicks=0,
                                       style={'border-width': '3px', 'font-size': '14px',
                                              'backgroundColor': kpmgBlue_hash, 'border-color': '#FFFFFF'}),
                            style={'margin-left': '45%', 'padding-top': '30px'}),
                        html.Div(id='output1')
                    ])
                ),
            ],
            id="modal",
            fullscreen=True,
            is_open=True,
        ),
    ]
)

layout = index_page
