##-------- LIBRARIES ----------------
from re import S
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

##-------- DEFINING VARIABLES ---------------


kpmgBlue_hash = '#00338D'

group_dummy = ["N/A"]
company_dummy = ["N/A"]
interest_group_dummy = ["Interest Expense", "Interest Income", "Interest Spare Capacity"]
tax_rates = [12.5, 25, 33]
currencies = ['Euro (€)', 'USD ($)']
column_names = ['Group', 'Company', 'Interest Type', 'Amount (€)', 'Tax Rate (%)', 'Legacy Debt',
                'PBI Amount (€)', 'Text Description']
ebc_df = pd.DataFrame(columns=column_names)

##-------------------------------EBC LAYOUT--------------------------------


# main card
card_ebc = dbc.Card(
    [
        dbc.CardBody([
            # title of card
            dbc.Row([
                dbc.Col([
                    html.Div([
                        
                        html.Div(html.H2("Exceeding Borrowing Costs", className="card-title", style={'color': kpmgBlue_hash}), style={'display': 'inline-block'}),
                        
                        html.Div(html.I(id="popover-target2", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left':'10px', 'display': 'inline-block'})
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
                        target="popover-target2",
                        trigger="hover"
                    ),
                        
                dbc.Col([
                    html.Div(
                        dbc.Button('Previous Page', href='/home',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
                dbc.Col([
                    html.Div(
                        dbc.Button('Next Page', href='/tax-ebitda',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
            ]),
            # html.H2("Exceeding Borrowing Costs", className="card-title", style={'color': kpmgBlue_hash}),

            html.Hr(style={'height': '3px'}),

            dbc.Row([
                # group name - dropdown
                dbc.Col([
                    html.H6("Group Name", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='ebc_group_dd',
                                     options=[{'label': grp, "value": grp} for grp in group_dummy],
                                     clearable=True,
                                     persistence=True,
                                     persistence_type='session',
                                     placeholder="Select Group..."),
                        style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                    )
                ], width=4
                ),

                dbc.Col([
                    # company name - dropdown
                    html.H6("Company Name", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='ebc_company_dd',
                                     clearable=True,
                                     persistence=True,
                                     persistence_type='session',
                                     placeholder="Select Company..."),
                        style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                    ),
                ], width=4),

                dbc.Col([
                    # interest group - dropdown
                    html.H6("Interest Type", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='ebc_interest_dd',
                                     options=[{'label': intgrp, "value": intgrp} for intgrp in interest_group_dummy],
                                     clearable=True,
                                     persistence=True,
                                     persistence_type='session',
                                     placeholder="Select Interest Type..."),
                        style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                    ),
                    html.H6(""),

                ], width=4)

            ]),

            html.Hr(style={'height': '2px'}),

            dbc.Row([
                dbc.Col([
                    html.H6(className="card-text", id='amount_description'),
                    dcc.Input(
                        style={'width': '80%'},
                        id="ebc_amount_input",
                        placeholder="Input Amount...",
                        type='number',
                        persistence=True,
                        persistence_type='session',
                        size="lg"
                    ),
                    html.H6(""),
                    dbc.Row([
                        dbc.Col(html.Div(id='ebc_amount_in_euro_text', style={'display': 'block'})),
                        dbc.Col(html.Div(id='ebc_amount_in_euro_value', style={'display': 'block'}))
                    ])

                ], width=4),

                dbc.Col([
                    html.H6("Tax Rate (%)", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='ebc_tax_dd',
                                     options=[{'label': rate, "value": rate} for rate in tax_rates],
                                     clearable=True,
                                     persistence=True,
                                     persistence_type='session',
                                     placeholder="Select Tax Rate..."),
                        style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                    ),

                ], width=4),

                dbc.Col([
                    html.H6("Legacy Debt"),
                    html.Div([
                        html.Div(html.H6("No"), id="ebc_legacy_no",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),
                        html.Div(
                            daq.ToggleSwitch(
                                id='ebc_legacy_toggle_switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash,
                                persistence=True,
                                persistence_type='session',
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),
                        html.Div(html.H6("Yes"), id="ebc_legacy_yes",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),
                    ]
                    ),

                ], width=4),

            ]),

            # amount - input box

            html.Hr(style={'height': '2px'}),

            dbc.Row([

                dbc.Col([
                    html.H6(id='pbi_description_currency', className="card-text"),
                    html.Div([

                        html.Div(html.H6("No"), id="ebc_pbi_no",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),

                        html.Div(
                            daq.ToggleSwitch(
                                id='ebc_pbi_toggle_switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash,
                                persistence=True,
                                persistence_type='session'
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),
                        html.Div(html.H6("Yes"), id="ebc_pbi_yes",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),
                    ]
                    ),
                    html.Div(
                        [
                            html.H6("", className="card-text"),
                            dcc.Input(
                                style={'width': '80%'},
                                id="ebc_pbi_input",
                                placeholder="Input PBI Amount...",
                                type='number',
                                persistence=True,
                                persistence_type='session',
                                size="lg"
                            )
                        ],
                        style={'display': 'block', 'width': '100%', 'border': '#8B0000', 'border-width': '5px'}),

                    html.H6(""),
                    dbc.Row([
                        dbc.Col(html.Div(id='ebc_pbi_amount_in_euro_text', style={'display': 'block'})),
                        dbc.Col(html.Div(id='ebc_pbi_amount_in_euro_value', style={'display': 'block'}))
                    ])

                ], width=4),

                dbc.Col([
                    html.Div([
                        html.H6("Description", className="card-text"),
                        html.P(""),
                        dcc.Input(
                            style={'width': '100%'},
                            id="ebc_text_description",
                            placeholder="Free Text Description...",
                            type='text',
                            persistence=True,
                            persistence_type='session',
                        ),
                    ],
                        style={"width": "90%", 'border': '#8B0000', 'border-width': '5px'})

                ], width=8),
            ]),

            html.Hr(style={'height': '2px'}),

            dbc.Row([
                # button to save details into table, and display this table

                dbc.Col([dbc.Button("Save & Add Details", id='save_ebc', n_clicks=0,
                                    style={'backgroundColor': kpmgBlue_hash, 'width': '100%'})], width=4),
            ]),
        ])
    ],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

# data table to store details
ebc_table_section = dbc.Card([
    dbc.CardBody([
        dbc.Row(html.H4("Details Inputted", className="card-text", style={'color': kpmgBlue_hash})),

        dbc.Row(
            dash_table.DataTable(
                id='ebc_table',
                editable=True,
                columns=[
                    {'name': 'Group', 'id': 'Group', 'editable': False},
                    {'name': 'Company', 'id': 'Company', 'editable': False},
                    {'name': 'Interest Type', 'id': 'Interest Type', 'editable': False},
                    {'name': 'Amount (€)', 'id': 'Amount (€)', 'editable': True, 'type': 'numeric'},
                    {'name': 'Tax Rate (%)', 'id': 'Tax Rate (%)', 'editable': True, 'type': 'numeric'},
                    {'name': 'Legacy Debt', 'id': 'Legacy Debt', 'editable': False},
                    {'name': 'PBI Amount (€)', 'id': 'PBI Amount (€)', 'editable': True, 'type': 'numeric'},
                    {'name': 'Text Description', 'id': 'Text Description', 'editable': True},
                ],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_cell={'textAlign': 'left'},
                style_header={'color': 'white', 'backgroundColor': 'rgb(0,51,141)', 'fontWeight': 'bold'},
                export_format="csv",
                persistence=True,
                persistence_type='session',
                row_deletable=True,
            )
        )
    ])
],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

# data table to store details
ebc_results_table_section = dbc.Card([
    dbc.CardBody([
        dbc.Row(html.H4("Results", className="card-text", style={'color': kpmgBlue_hash})),

        dbc.Row(
            dash_table.DataTable(
                id='ebc_results_table',
                editable=True,
                columns=[
                    {'name': 'Group', 'id': 'Group', 'editable': False},
                    {'name': 'Company', 'id': 'Company', 'editable': False},
                    {'name': 'Exceeding Borrowing Costs (€)', 'id': 'Exceeding Borrowing Costs', 'editable': False},
                    {'name': 'Exceeding Borrowing Costs for De Minimis Exemption (€)',
                     'id': 'Exceeding Borrowing Costs for De Minimis Exemption', 'editable': False},
                ],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_cell={'textAlign': 'left'},
                style_header={'color': 'white', 'backgroundColor': 'rgb(0,51,141)', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{Company} = "Group Total"'
                        },
                        'backgroundColor': 'rgba(0, 163, 160, 0.1)'
                    }
                ],
                export_format="csv",
                persistence=True,
                persistence_type='session',
                # row_deletable=True,
            )
        )
    ])
],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

ebc_workings_card = html.Div([
    dbc.Card(
        [
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.H4("Workings", className="card-text", style={'color': kpmgBlue_hash})),
                    dbc.Col([
                        html.H6("Select Company", className="card-text"),
                        html.Div(
                            dcc.Dropdown(id='ebc_company_workings_dd',
                                         # options=[{'label': grp, "value": grp} for grp in group_dummy],
                                         clearable=True,
                                         persistence=True,
                                         persistence_type='session',
                                         placeholder="Select Group..."),
                            style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                        )
                    ]),
                ]),
                html.Hr(style={'height': '2px'}),
                # html.Hr(style={'height': '2px'}),
                # html.Hr(),
                dbc.Row([
                    dbc.Col(html.H5("Exceeding Borrowing Costs"), width=6),
                    dbc.Col(html.H5("Exceeding Borrowing Costs for the De Minimis Exemption"), width=6),
                ]),

                dbc.Row([
                    dbc.Col([
                        html.H6(html.B("Workings")),
                        html.Div(id='ebc-workings-output'),
                    ], width=6),

                    dbc.Col([
                        html.H6(html.B("Workings")),
                        html.Div(id='ebc-dm-workings-output'),
                    ], width=6)
                ])

            ])
        ],
        color="light",
        style={"margin-left": "5rem", "width": "70rem"}
    )
])

layout = html.Div([
    card_ebc,
    html.P(""),
    ebc_table_section,
    html.P(""),
    ebc_results_table_section,
    html.P(""),
    ebc_workings_card
])


