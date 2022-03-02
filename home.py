import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd


corporate_tax = 12.5
kpmgBlue_hash = '#00338D'
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server


home_df = pd.DataFrame(columns=['Group', 'Company', 'In Interest Group?'])
currencies = ['Euro (€)', 'USD ($)', 'GBP (£)', 'Other']

# CREATING CARD WHERE USER INPUTS DETAILS
home_card_question = dbc.Card(
    [
        dbc.CardBody([

            # title of card
            dbc.Row([
                dbc.Col([
                    html.Div([
                        
                        html.Div(html.H2("Initial Setup", className="card-title", style={'color': kpmgBlue_hash}), style={'display': 'inline-block'}),
                        
                        html.Div(html.I(id="popover-target", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left':'10px', 'display': 'inline-block'})
                        ])
                    ], width=9),
                    
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
                        target="popover-target",
                        trigger="hover"
                    ),
                
                dbc.Col([
                    html.Div(
                        dbc.Button('Next Page', href='/exceeding-borrowing-costs',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
            ]),
            html.Hr(style={'height': '3px'}),

            ##---FIRST ROW---

            dbc.Row([

                # Group Name Input Box
                dbc.Col([
                    html.H5("Group Name", className="card-text"),
                    html.Div(
                        dcc.Input(
                            style={'width': '80%'},
                            id="group",
                            placeholder="Enter Group Name...",
                            size="lg",
                            persistence=True,
                            persistence_type='session'
                        ),
                    ),
                ], width=6),

                # Company Name Input Box
                dbc.Col([
                    html.H5("Company Name", className="card-text"),
                    html.Div(
                        dcc.Input(
                            style={'width': '80%'},
                            id="company",
                            placeholder="Enter Company Name...",
                            size="lg"
                        ),
                    ),
                ], width=6),
            ]),

            html.Hr(style={'height': '2px'}),

            ##---SECOND ROW---
            dbc.Row([

                # Is it a company? Toggle switch
                dbc.Col([
                    html.H5("Is it a company?"),
                    html.Div([
                        html.Div(html.H6("No"), id='company_no',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),
                        html.Div(
                            daq.ToggleSwitch(
                                id='company-toggle-switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),
                        html.Div(html.H6("Yes"), id='company_yes',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),

                        html.Div(html.H6(html.B("Outside of scope"), style={'color': kpmgBlue_hash}),
                                 id='outside_scope_company',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw',
                                        'margin-top': '1vw'}),
                    ]),
                ], width=6),

                # chargeable to corporation tax - Toggle Switch
                dbc.Col([
                    html.H5("Is it a chargeable to corporation tax?"),
                    html.Div([
                        html.Div(html.H6("No"), id='chargeable_no',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),
                        html.Div(
                            daq.ToggleSwitch(
                                id='chargeable-toggle-switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),

                        html.Div(html.H6("Yes"), id='chargeable_yes',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),

                        html.Div(html.H6(html.B("Outside of scope"), style={'color': kpmgBlue_hash}),
                                 id='outside_scope_chargeable',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw',
                                        'margin-top': '1vw'})
                    ]),
                ], width=6),
            ]),

            html.Br(),

            ##---THIRD ROW---
            dbc.Row([
                # standalone - Toggle Switch
                dbc.Col([
                    html.H5("Is it a standalone entity?"),
                    html.Div([
                        html.Div(html.H6("No"), id='standalone_no',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),
                        html.Div(
                            daq.ToggleSwitch(
                                id='standalone-toggle-switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash,
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),
                        html.Div(html.H6("Yes"), id='standalone_yes',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),
                        html.Div(html.H6(html.B("Outside of scope"), style={'color': kpmgBlue_hash}),
                                 id='outside_scope_standalone',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw',
                                        'margin-top': '1vw'})
                    ]),
                ], width=6),
                # interest group - toggle switch
                dbc.Col([
                    html.H5("Is it in an interest group?"),
                    html.Div([
                        html.Div(html.H6("No"), id='ig_no',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),
                        html.Div(
                            daq.ToggleSwitch(
                                id='interest-group-toggle-switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash,
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),
                        html.Div(html.H6("Yes"), id='ig_yes',
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),
                    ]),
                ], width=6),
            ]),

            html.Hr(style={'height': '2px'}),

            dbc.Row([
                dbc.Col([
                    html.H5("Currency Used", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='currency_dd',
                                     options=[{'label': currency, "value": currency} for currency in currencies],
                                     clearable=True,
                                     persistence=True,
                                     persistence_type='session',
                                     value='Euro (€)'),
                        style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                    ),
                    html.Div([
                        html.H6(""),
                        dcc.Input(
                            style={'width': '80%'},
                            id="spot_rate_input",
                            placeholder="Input Spot Rate...",
                            type='number',
                            persistence=True,
                            persistence_type='session',
                            size="lg"
                        )
                    ], style={'display': 'block', 'border': '#8B0000', 'border-width': '5px'}
                    )
                ], width=6)
            ]),

            html.Hr(style={'height': '2px'}),

            dbc.Row([
                dbc.Col(dbc.Button("Save & Add Details", id='clear_output', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}), width=4),
            ])
        ])
    ], color="light", style={"margin-left": "5rem", "width": "70rem"}
)

##############################
# Data Table to store details of Initial Setup
home_table_section = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row(html.H4("Data Table", className="card-text", style={'color': kpmgBlue_hash})),
            dbc.Row(
                dash_table.DataTable(
                    id='home_table',
                    columns=[{"name": i, "id": i} for i in home_df.columns],
                    style_cell={'textAlign': 'left', 'height': 'auto', 'minWidth': '120px', 'width': '120px',
                                'maxWidth': '120px'},
                    style_header={'color': 'white', 'backgroundColor': 'rgb(0,51,141)', 'fontWeight': 'bold'},
                    export_format="csv",
                    row_deletable=True,
                    persistence=True,
                    persistence_type='session'
                )
            )

        ])
    ],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

layout = html.Div([
    home_card_question,
    html.P(""),
    home_table_section,
])


