##-------- LIBRARIES ----------------
import dash
from dash import html
import dash_bootstrap_components as dbc

corporate_tax = 12.5
kpmgBlue_hash = '#00338D'
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server
##-------------------------------SUMMARY LAYOUT--------------------------


summary_card = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([

                        html.Div(html.H2("Summary", className="card-title", style={'color': kpmgBlue_hash}),
                                 style={'display': 'inline-block'}),

                        html.Div(html.I(id="popover-target7", className="bi bi-info-circle-fill me-2",
                                        style={'display': 'inline-block'}),
                                 style={'margin-left': '10px', 'display': 'inline-block'})
                    ])
                ], width=10),

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
                    target="popover-target7",
                    trigger="hover"
                ),
                dbc.Col([
                    html.Div(
                        dbc.Button('Previous Page', href='/disallowance-formula',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
            ]),

            html.Hr(style={'height': '3px'}),

            html.Div([
                html.H5('Exceeding Borrowing Costs'),
                # html.Div(id= 'ebc-table-summary'),
                # dbc.Button("Calculate", id='summary-ebc-calculate', n_clicks=0,  style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}),
                html.Div(id='summary-borrowing-calc-output'),
                html.Div(id='summary-borrowing-calc-output-dm'),

            ]),
            html.P(""),
            html.Hr(style={'height': '2px'}),

            html.Div([
                html.H5('Tax EBITDA'),
                html.Div(id='summary-tax-ebitda-output'),
            ]),
            html.P(""),
            html.Hr(style={'height': '2px'}),

            html.Div([
                html.H5('Group Ratio'),
                html.Div(id='summary-group-ratio-output'),
            ]),
            html.P(""),
            html.Hr(style={'height': '2px'}),

            html.Div([
                html.H5('Equity Ratio'),
                html.Div(id='summary-equity-ratio-output-group'),
                html.Div(id='summary-equity-ratio-output-worldwide')
            ]),
            html.P(""),
            html.Hr(style={'height': '2px'}),

            # subsection to show disallowance formula results
            html.Div([
                dbc.Col([
                    html.H5('Disallowance Formula'),
                    html.Div(id='summary-disallowance-output')
                ])
            ]),
            html.P(""),

        ],
        )
    ],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

layout = summary_card