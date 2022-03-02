from re import S
# from selectors import EpollSelector
from ssl import DefaultVerifyPaths
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import pandas as pd
from dash.exceptions import PreventUpdate

corporate_tax = 12.5
kpmgBlue_hash = '#00338D'
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server

##-------------------------------DISALLOWANCE LAYOUT--------------------------

# card to test if disallowance is applied, which tests are passed etc
disallowance_card = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([

                        html.Div(
                            html.H2("Disallowance Formula", className="card-title", style={'color': kpmgBlue_hash}),
                            style={'display': 'inline-block'}),

                        html.Div(html.I(id="popover-target6", className="bi bi-info-circle-fill me-2",
                                        style={'display': 'inline-block'}),
                                 style={'margin-left': '10px', 'display': 'inline-block'})
                    ])
                ], width=8),

                dbc.Popover(
                    [
                        dbc.PopoverHeader("Definition:"),
                        dbc.PopoverBody(
                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                            "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute "
                            "irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
                            "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
                            "deserunt mollit anim id est laborum."),
                    ],
                    id="popover",
                    is_open=False,
                    target="popover-target6",
                    trigger="hover"
                ),
                dbc.Col([
                    html.Div(
                        dbc.Button('Previous Page', href='/equity-ratio',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
                dbc.Col([
                    html.Div(
                        dbc.Button('Next Page', href='/summary',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
            ]),

            html.Hr(style={'height': '3px'}),

            ## EQUITY WITHIN/OUTSIDE
            html.H5("Equity Ratio Test",
                    className="card-text"),
            dbc.Row([
                dbc.Col([
                    html.Div(id="equityRatioGrpCalc"),
                    html.Div(id="equityRatioWrldCalc")

                ], width=5),
                dbc.Col([
                    html.Div(id="within-output")
                ], width=7),
            ]),

            html.Hr(style={'height': '2px'}),

            ## EBCDM SCOPE
            html.H5("De Minimis Exemption Test",
                    className="card-text"),
            dbc.Row([
                dbc.Col([
                    html.Div(id="deMinimis"),
                ], width=5),
                dbc.Col([
                    html.Div(id="scope-output")
                ], width=7),
            ]),

            html.Hr(style={'height': '2px'}),

            # Gross profit
            html.H5("Exceeding Borrowing Costs Test", className="card-text"),
            dbc.Row([
                dbc.Col([
                    html.Div(id="ebctest"),
                ], width=5),
                dbc.Col([
                    html.Div(id="sign-output")
                ], width=7),
            ]),

        ],
        )
    ],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

# card to show workings
disallowance_workings_card = html.Div([
    dbc.Card(
        [
            dbc.CardBody([
                dbc.Row(html.H4("Results", className="card-text", style={'color': kpmgBlue_hash})),
                html.Hr(style={'height': '2px'}),

                dbc.Row(html.H5("Disallowance Formula")),
                html.Div(id='dis-values', style={'display': 'block'}),

                html.Div(id='dis-output'),
                html.Hr(),
                dbc.Row(html.H5("Disallowance Workings")),
                dbc.Row([

                    dbc.Col([

                        html.Div(id='dis-workings-output'),
                        html.P(""),
                    ]),
                ]),

            ])
        ],
        color="light",
        style={"margin-left": "5rem", "width": "70rem"}
    )
]

)

layout = html.Div([
    disallowance_card,
    html.P(""),
    disallowance_workings_card
]),

