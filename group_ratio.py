##-------- LIBRARIES ----------------
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

corporate_tax = 12.5
kpmgBlue_hash = '#00338D'
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server

##-------------------------------GROUP RATIO VARIABLES--------------------------

tax_rates = [12.5, 25, 33, 'Other']

##-------------------------------GROUP RATIO LAYOUT--------------------------


# CREATING CARD WHERE USER INPUTS DETAILS
gr_card_question = dbc.Card(
    [
        dbc.CardBody([
            # title of card
            dbc.Row([
                dbc.Col([
                    html.Div([

                        html.Div(html.H2("Group Ratio", className="card-title", style={'color': kpmgBlue_hash}),
                                 style={'display': 'inline-block'}),

                        html.Div(html.I(id="popover-target4", className="bi bi-info-circle-fill me-2",
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
                    target="popover-target4",
                    trigger="hover"
                ),
                dbc.Col([
                    html.Div(
                        dbc.Button('Previous Page', href='/tax-ebitda',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
                dbc.Col([
                    html.Div(
                        dbc.Button('Next Page', href='/equity-ratio',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
            ]),
            # html.H2("Group Ratio", className="card-title",style={'color':kpmgBlue_hash}),
            html.Hr(style={'height': '3px'}),

            # Gross profit
            html.H5("Worldwide Group Net Finance Expense From Consolidated Financial Statements",
                    style={'font-size': '100%'},
                    className="card-text"),
            dcc.Input(
                id="inputA",
                placeholder="Input Amount...",
                type='number',
                size="lg",
                persistence=True,
                persistence_type='session'
            ),
            html.P(""),

            # Gross profit
            html.H5("Worldwide Group EBITDA From Consolidated Financial Statements", style={'font-size': '100%'},
                    className="card-text"),
            dcc.Input(
                id="inputB",
                placeholder="Input Amount...",
                type='number',
                size="lg",
                persistence=True,
                persistence_type='session'

            ),

            html.P(""),

            html.P(""),
        ]),
    ],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

gr_results_card = html.Div([
    dbc.Card(
        [
            dbc.CardBody([

                dbc.Row(html.H4("Results", className="card-text", style={'color': kpmgBlue_hash})),
                html.Hr(style={'height': '2px'}),

                html.H5("Group Ratio"),
                html.P(""),
                dbc.Row([
                    dbc.Col([

                        html.H6(html.B("Amount")),

                        # dbc.Button("Calculate", id='gr-calculate-button', n_clicks=0,
                        #            style={'backgroundColor': kpmgBlue_hash, 'width': '80%'}),
                        # html.P(""),
                        html.Div(id='group_ratio_output'),

                    ], width=4),

                ]),

                # html.Br(),
                html.Hr(),
                # html.Br(),
                html.H6(html.B("Workings")),
                html.Div(id='group_ratio_workings'),

            ])
        ],
        color="light",
        style={"margin-left": "5rem", "width": "70rem"}
    )
]

)

layout = html.Div([
    gr_card_question,
    html.P(""),
    gr_results_card,
    html.P(""),
    html.P("")
])
