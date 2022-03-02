##-------- LIBRARIES ----------------
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq

corporate_tax = 12.5
kpmgBlue_hash = '#00338D'
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server

##-------------------------------EQUITY RATIO LAYOUT--------------------------

# CREATING CARD WHERE USER INPUTS DETAILS
er_card_question = dbc.Card(
    [
        dbc.CardBody([
            # title of card
            dbc.Row([
                dbc.Col([
                    html.Div([

                        html.Div(html.H2("Equity Ratio", className="card-title", style={'color': kpmgBlue_hash}), style={'display': 'inline-block'}),

                        html.Div(html.I(id="popover-target5", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left' :'10px', 'display': 'inline-block'})
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
                    target="popover-target5",
                    trigger="hover"
                ),
                dbc.Col([
                    html.Div(
                        dbc.Button('Previous Page', href='/group-ratio',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
                dbc.Col([
                    html.Div(
                        dbc.Button('Next Page', href='/disallowance-formula',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
            ]),

            # html.H2("Equity Ratio", className="card-title",style={'color':kpmgBlue_hash}),
            html.Hr(style={'height': '3px'}),

            html.H5("Single Company Worldwide Group", style={'font-size': '100%'}, className="card-text"),

            html.Div([

                html.Div(html.H6("No"), id="eq_no",
                         style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw'
                             , 'margin-top': '0.1vw'}),

                html.Div(
                    daq.ToggleSwitch(
                        id='eq_toggle_switch',
                        value=False,
                        size=35,
                        color=kpmgBlue_hash,
                        persistence=True,
                        persistence_type='session',
                    ),
                    style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                           'margin-top': '0.1vw'}
                ),
                html.Div(html.H6("Yes"), id="eq_yes",
                         style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                'margin-top': '0.1vw'}),
            ]
            ),

            html.Hr(style={'height': '2px'}),

            dbc.Row([
                dbc.Col([
                    html.H5("Interest Group Equity", style={'font-size': '100%'},
                            className="card-text"),
                    dcc.Input(
                        id="inputE",
                        placeholder="Input Amount...",
                        persistence=True,
                        persistence_type='session',
                        type='number',
                        size="lg"
                    ),
                ], width=3),

                dbc.Col([
                    html.H5("Debt From Associated Enterprises", id="debt_assoc_enterprise_title",
                            style={'font-size': '100%', 'display': 'none'},
                            className="card-text"),
                    dcc.Input(
                        id="debt_assoc_enterprise",
                        placeholder="Input Amount...",
                        persistence=True,
                        persistence_type='session',
                        type='number',
                        size="lg",
                        style={'display': 'none'}
                    ),
                ], width=4),
            ]),

            html.P(""),

            html.H5("Interest Group Total Assets", style={'font-size': '100%'},
                    className="card-text"),
            dcc.Input(
                id="inputF",
                placeholder="Input Amount...",
                persistence=True,
                persistence_type='session',
                type='number',
                size="lg"
            ),

            html.Hr(style={'height': '2px'}),

            # Worldwide gross profit
            html.H5("Worldwide Group Equity From Consolidated Financial Statements", style={'font-size': '100%'},
                    className="card-text"),
            dcc.Input(
                id="inputC",
                placeholder="Input Amount...",
                persistence=True,
                persistence_type='session',
                type='number',
                size="lg"
            ),
            html.P(""),

            # Worldwide gross profit
            html.H5("Worldwide Group Total Assets From Consolidated Financial Statements", style={'font-size': '100%'},
                    className="card-text"),
            dcc.Input(
                id="inputD",
                placeholder="Input Amount...",
                persistence=True,
                persistence_type='session',
                type='number',
                size="lg"
            ),
        ]),
    ],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

er_results_card = html.Div([
    dbc.Card(
        [
            dbc.CardBody([
                html.H4("Results", className="card-text", style={'color': kpmgBlue_hash}),
                html.Hr(style={'height': '2px'}),

                dbc.Row([
                    dbc.Col(html.H5(["Interest Group Equity /", html.Br(), "Interest Group Total Assets"]), width=6),
                    dbc.Col(html.H5(["Worldwide Group Equity /", html.Br(), "Worldwide Group Total Assets"]), width=6)
                ]),

                # html.P(""),
                dbc.Row([
                    dbc.Col([
                        html.H6(html.B("Amount")),
                        html.Div(id='er_outputA'),
                        html.P(""),
                    ], width=6),

                    dbc.Col([
                        html.H6(html.B("Amount")),
                        html.Div(id='er_outputB'),
                        html.P(""),
                    ], width=6),

                ]),

                html.Hr(),

                dbc.Row([
                    dbc.Col([
                        html.H6(html.B("Workings")),
                        html.Div(id='er_workingsA'),
                        html.P(""),
                    ], width=6),

                    dbc.Col([
                        html.H6(html.B("Workings")),
                        html.Div(id='er_workingsB'),
                        html.P(""),
                    ], width=6),

                ]),
            ])
        ],
        color="light",
        style={"margin-left": "5rem", "width": "70rem"}
    )
]

)

layout = html.Div([
    er_card_question,
    html.P(""),
    er_results_card,
    html.P("")

])

