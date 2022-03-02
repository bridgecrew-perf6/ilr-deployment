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

##-------------------------------TAX EBITDA VARIABLES--------------------------


group_dummy = ["A", "B", "C"]
company_dummy = ["Ryanair", "Aer Lingus", "KPMG"]
interest_group_dummy = ["Relevant Profits (Taxable Profits)", "Relevant Profits - Credit adjustment",
                        "Foreign Tax Deductions",
                        "Capital Allowances", "Balancing Charges",
                        "Capital Element Of Deductible Finance Lease Payment",
                        "Limitation Spare Capacity Carried Forward"]
tax_rates = [12.5, 25, 33]

column_names1 = ['Group', 'Company', 'EBITDA Category', 'Amount (€)', 'Tax Rate (%)', 'Loss (€)',
                 'PBIE (€)', 'Deductible Interest (€)']
ebitda_df = pd.DataFrame(columns=column_names1)

##-------------------------------TAX EBITDA LAYOUT-----------------------------


# main card
card_tax_ebitda = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([

                        html.Div(html.H2("Tax EBITDA", className="card-title", style={'color': kpmgBlue_hash}),
                                 style={'display': 'inline-block'}),

                        html.Div(html.I(id="popover-target3", className="bi bi-info-circle-fill me-2",
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
                    target="popover-target3",
                    trigger="hover"
                ),
                dbc.Col([
                    html.Div(
                        dbc.Button('Previous Page', href='/exceeding-borrowing-costs',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),
                dbc.Col([
                    html.Div(
                        dbc.Button('Next Page', href='/group-ratio',
                                   style={'width': '85%', 'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        , style={'text-align': 'right'})
                ]),

            ]),
            html.Hr(style={'height': '3px'}),

            dbc.Row([
                # group name - dropdown
                dbc.Col([html.H5("Group Name", className="card-text", style={'font-size': '100%'}),
                         html.Div(
                             dcc.Dropdown(id='group_name_ebitda',
                                          options=[{'label': grp, "value": grp} for grp in group_dummy],
                                          clearable=True,
                                          persistence=True,
                                          persistence_type='session',
                                          placeholder="Select Group... "),
                             style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}),
                         ], width=4),

                # company name - dropdown
                dbc.Col([html.H5("Company Name", className="card-text", style={'font-size': '100%'}),
                         html.Div(
                             dcc.Dropdown(id='company_name_ebitda',
                                          options=[{'label': cmp, "value": cmp} for cmp in company_dummy],
                                          clearable=True,
                                          persistence=True,
                                          persistence_type='session',
                                          placeholder="Select Company..."),
                             style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}),
                         ], width=4),

                # interest group - dropdown
                dbc.Col([html.H5("EBITDA Category", className="card-text", style={'font-size': '100%'}),
                         html.Div(
                             dcc.Dropdown(id='interest_group_ebitda',
                                          options=[{'label': intgrp, "value": intgrp} for intgrp in
                                                   interest_group_dummy],
                                          clearable=True,
                                          persistence=True,
                                          persistence_type='session',
                                          placeholder="Select Category..."),
                             style={"width": "80%", 'verticalAlign': 'middle', 'border': '#8B0000',
                                    'border-width': '5px'}),
                         ], width=4),
            ], align="center"),
            html.Hr(style={'height': '2px'}),

            dbc.Row([
                # amount - input box
                dbc.Col([
                    html.H6(className="card-text", id='ebitda_amount_description'),
                    html.Div(
                        dcc.Input(
                            style={'width': '80%'},
                            id="amount_input_ebitda",
                            placeholder="Input Amount...",
                            persistence=True,
                            type='number',
                            persistence_type='session',
                            size="lg"),
                    ),

                    html.H6(""),
                    dbc.Row([
                        dbc.Col(html.Div(id='ebitda_amount_in_euro_text', style={'display': 'block'})),
                        dbc.Col(html.Div(id='ebitda_amount_in_euro_value', style={'display': 'block'}))
                    ]),

                ], width=4),

                dbc.Col([
                    html.H5("Is this referring to a loss?", className="card-text", style={'font-size': '100%'}),
                    html.Div([

                        html.Div(html.H6("No"), id="ebitda_loss_no",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),

                        html.Div(
                            daq.ToggleSwitch(
                                id='ebitda_loss_toggle_switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash,
                                persistence=True,
                                persistence_type='session'
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),
                        html.Div(html.H6("Yes"), id="ebitda_loss_yes",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),
                    ]),
                ], width=4),

                # tax rate - drop down
                dbc.Col([html.H5("Tax Rate (%)", className="card-text", style={'font-size': '100%'}),
                         html.Div(
                             dcc.Dropdown(id='tax_rate_ebitda',
                                          options=[{'label': rate, "value": rate} for rate in tax_rates],
                                          clearable=True,
                                          persistence=True,
                                          persistence_type='session',
                                          placeholder="Select Tax Rate..."),
                             style={'width': '80%', 'border': '#8B0000', 'border-width': '5px'})
                         #  style={'width': '6%', 'display': 'table-cell', 'padding': 5, 'verticalAlign': 'middle'}),
                         ], width=4),

            ]),
            html.Hr(style={'height': '2px'}),

            dbc.Row([
                dbc.Col([
                    html.H6(className="card-text", id='ebitda_pbi_description'),
                    html.Div([
                        html.Div(html.H6("No"), id="ebitda_pbi_no",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),

                        html.Div(
                            daq.ToggleSwitch(
                                id='ebitda_pbi_toggle_switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash,
                                persistence=True,
                                persistence_type='session'
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),

                        html.Div(html.H6("Yes"), id="ebitda_pbi_yes",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),
                    ]), ], width=4),

                dbc.Col([html.H6(className="card-text", id='ebitda_pbi_ded_description'),
                         html.Div([
                             html.Div(html.H6("No"), id="ebitda_pbi_ded_no",
                                      style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                             'margin-top': '1vw'}),

                             html.Div(
                                 daq.ToggleSwitch(
                                     id='ebitda_pbi_ded_toggle_switch',
                                     value=False,
                                     size=35,
                                     color=kpmgBlue_hash,
                                     persistence=True,
                                     persistence_type='session'
                                 ),
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}
                             ),

                             html.Div(html.H6("Yes"), id="ebitda_pbi_ded_yes",
                                      style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                             'margin-top': '1vw'}),
                         ]), ]),
                dbc.Row([

                    dbc.Col([
                        html.Div(
                            dcc.Input(
                                style={'width': '80%'},
                                id="input_pbipp_ebitda",
                                placeholder="Input Amount...",
                                # value = 0,
                                persistence=True,
                                type='number',
                                persistence_type='session',
                                size="lg"),
                        ),

                        html.H6(""),
                        dbc.Row([
                            dbc.Col(html.Div(id='ebitda_pbi_amount_in_euro_text', style={'display': 'block'})),
                            dbc.Col(html.Div(id='ebitda_pbi_amount_in_euro_value', style={'display': 'block'}))
                        ]),

                    ], width=4),

                    dbc.Col([
                        html.Div(
                            dcc.Input(

                                style={'width': '80%'},
                                id="input_deduct_ebitda",
                                placeholder="Input PBI Deductible Interest...",
                                persistence=True,
                                type='number',
                                persistence_type='session',
                                size="lg",
                                value='0'
                            ),
                        ),

                        html.H6(""),
                        dbc.Row([
                            dbc.Col(html.Div(id='ebitda_pbi_interest_amount_in_euro_text', style={'display': 'block'})),
                            dbc.Col(html.Div(id='ebitda_pbi_interest_amount_in_euro_value', style={'display': 'block'}))
                        ]),

                    ], width=4),
                ])

            ]),

            html.Hr(style={'height': '2px'}),
            html.P(""),
            dbc.Row([
                # button to save details into table, and display this table
                dbc.Col(dbc.Button("Save & Add Details", id='save_tax_ebitda', n_clicks=0,
                                   style={'width': '100%', 'verticalAlign': 'middle', 'backgroundColor': kpmgBlue_hash})
                        , width=4),

            ], align="center"),
        ])
    ],
    color="light",
    style={"margin-left": "5rem", "width": "70rem"}
)

# data table to store details
ebitda_table_section = dbc.Card([
    dbc.CardBody([
        dbc.Row(html.H4("Details Inputted", className="card-text", style={'color': kpmgBlue_hash})),
        dbc.Row(
            dash_table.DataTable(
                id='ebitda_table',
                editable=True,
                columns=[
                    {'name': 'Group', 'id': 'Group', 'editable': False},
                    {'name': 'Company', 'id': 'Company', 'editable': False},
                    {'name': 'EBITDA Category', 'id': 'EBITDA Category', 'editable': False},
                    {'name': 'Amount (€)', 'id': 'Amount (€)', 'editable': True, 'type': 'numeric'},
                    {'name': 'Tax Rate (%)', 'id': 'Tax Rate (%)', 'editable': True, 'type': 'numeric'},
                    {'name': 'Loss (€)', 'id': 'Loss (€)', 'editable': True, 'type': 'numeric'},
                    {'name': 'PBIE (€)', 'id': 'PBIE (€)', 'editable': True, 'type': 'numeric'},
                    {'name': 'Deductible Interest (€)', 'id': 'Deductible Interest (€)', 'editable': True,
                     'type': 'numeric'}],
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

ebitda_results_table_section = dbc.Card([
    dbc.CardBody([
        dbc.Row(html.H4("Results", className="card-text", style={'color': kpmgBlue_hash})),
        dbc.Row(
            dash_table.DataTable(
                id='ebitda_results_table',
                editable=True,
                columns=[
                    {'name': 'Group', 'id': 'Group', 'editable': False},
                    {'name': 'Company', 'id': 'Company', 'editable': False},
                    {'name': 'Tax EBITDA (€)', 'id': 'Tax EBITDA', 'editable': False},

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
                ##data=ebitda_df.to_dict('records'),
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

ebitda_results_card = html.Div([
    dbc.Card(
        [
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.H4("Workings", className="card-text", style={'color': kpmgBlue_hash})),
                    dbc.Col([
                        html.H6("Select Company", className="card-text"),
                        html.Div(
                            dcc.Dropdown(id='ebitda_company_workings_dd',
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
                dbc.Row(html.H5("Tax EBITDA")),

                html.H6(html.B("Workings")),
                html.Div(id='ebitda_workings_output'),
                html.P(""),
            ]),
        ],
        color="light",
        style={"margin-left": "5rem", "width": "70rem"}
    )
])

layout = html.Div([
    card_tax_ebitda,
    html.P(""),
    ebitda_table_section,
    html.P(""),
    ebitda_results_table_section,
    html.P(""),
    ebitda_results_card
])
