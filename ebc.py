##-------- LIBRARIES ----------------
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd

dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server

##-------- DEFINING VARIABLES ---------------


kpmgBlue_hash = '#00338D'
group_dummy = ["N/A"]
company_dummy = ["N/A"]
interest_group_dummy = ["Interest Expense", "Interest Income", "Interest Spare Capacity"]
tax_rates = [12.5, 25, 33]
# ebc_df = pd.DataFrame(columns = ['Group', 'Company', 'Interest Type', 'Amount (€)', 'Tax Rate (%)', 'Legacy Debt'])

data = {
    'Group': ['IAG', 'IAG', 'IAG', 'IAG', 'IAG', 'IAG', 'IAG', 'IAG'],
    'Company': ['Aerlingus', 'Aerlingus', 'Aerlingus', 'Aerlingus', 'Aerlingus', 'Aerlingus', 'Aerlingus', 'Aerlingus'],
    'Interest Type': ['Interest Expense', 'Interest Expense', 'Interest Expense', 'Interest Expense',

                      'Interest Income', 'Interest Income', 'Interest Income', 'Interest Spare Capacity'],
    'Amount (€)': [700, 20, 100, 100, 10, 10, 10, 20],
    'Tax Rate (%)': [12.5, 12.5, 25, 33, 12.5, 25, 33, ''],
    'Legacy Debt': ['N', 'Y', 'N', 'N', 'N', 'N', 'N', ''],
    'PBI Amount (€)': ['', '', '', '', '', '', '', ''],
    'Text Description': ['', '', '', '', '', '', '', '']

}

ebc_df = pd.DataFrame(data)

##--------------------------PAGE CONTENT ---------------------------------

# main card
card_ebc = dbc.Card(
    [
        dbc.CardBody([
            # title of card
            dbc.Row([
                dbc.Col([html.H2("Exceeding Borrowing Costs", className="card-title", style={'color': kpmgBlue_hash})], width=10),
                dbc.Col([
                        html.Div(
                        dbc.Button('Next Page', id='next-page-button', href='/tax-ebitda', style={'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
                        ,style={'text-align':'right'})
                    ]),
            ]),
            # html.H2("Exceeding Borrowing Costs", className="card-title", style={'color': kpmgBlue_hash}),

            html.Hr(style={'height': '3px'}),

            dbc.Row([
                # group name - dropdown
                dbc.Col([
                    html.H6("Group Name", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='group_dd',
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
                    #company name - dropdown
                    html.H6("Company Name", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='company_dd',
                                     # options=[{'label':cmp, "value":cmp} for cmp in company_dummy],
                                     clearable=True,
                                     persistence=True,
                                     persistence_type='session',
                                     placeholder="Select Company..."),
                        style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                    ),
                ], width=4),

                dbc.Col([
                    #interest group - dropdown
                    html.H6("Interest Type", className="card-text"),
                    html.Div(
                        dcc.Dropdown(id='interest_dd',
                                     options=[{'label': intgrp, "value": intgrp} for intgrp in interest_group_dummy],
                                     clearable=True,
                                     persistence=True,
                                     persistence_type='session',
                                     placeholder="Select Interest Type..."),
                        style={"width": "80%", 'border': '#8B0000', 'border-width': '5px'}
                    ),

                ], width=4)

            ]),

            html.Hr(style={'height': '2px'}),

            dbc.Row([
                dbc.Col([
                    html.H6("Amount (€)", className="card-text"),
                    dcc.Input(

                        style = {'width':'80%'},
                        id="amount_input",
                        placeholder="Input Amount...",
                        type ='number',
                        persistence=True,
                        persistence_type='session',
                        size="lg"
                    ),
                ], width=4),

                dbc.Col([
                       #tax rate - drop down
                        #html.Hr(style={'height': '2px'}),
                        html.H6("Tax Rate (%)", className="card-text"),
                        html.Div(
                                dcc.Dropdown(id='tax_dd',
                                        options=[{'label':rate, "value":rate} for rate in tax_rates],
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

                        html.Div(html.H6("No"), id="legacy_no",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '0vw',
                                        'margin-top': '1vw'}),

                        html.Div(
                            daq.ToggleSwitch(
                                id='legacy_toggle_switch',
                                value=False,
                                size=35,
                                color=kpmgBlue_hash,
                                persistence=True,
                                persistence_type='session',
                            ),
                            style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                   'margin-top': '1vw'}
                        ),
                        html.Div(html.H6("Yes"), id="legacy_yes",
                                 style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw',
                                        'margin-top': '1vw'}),
                    ]
                    ),

                ], width=4)

            ]),

            # amount - input box

            html.Hr(style={'height': '2px'}),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Public Benefit Infrastructure (€)", className="card-text"),
                        dcc.Input(
                            style={'width': '80%'},
                            id="pbi_input",
                            placeholder="Input PBI Amount...",
                            type='number',
                            persistence=True,
                            persistence_type='session',
                            size="lg"
                        ),
                    ],
                        style={"width": "100%", 'border': '#8B0000', 'border-width': '5px'})

                ], width=4),

                dbc.Col([
                    html.Div([
                        html.H6("Description", className="card-text"),
                        dcc.Input(
                            style={'width': '100%'},
                            id="text_description",
                            placeholder="Free Text Description...",
                            type='text',
                            persistence=True,
                            persistence_type='session',
                        ),
                    ],
                        style={"width": "100%", 'border': '#8B0000', 'border-width': '5px'})

                ], width=8),
            ]),

            html.Hr(style={'height': '2px'}),

            #legacy debt - toggle switch
            
            #html.P(""), 

            dbc.Row([
                # button to save details into table, and display this table
                dbc.Col([dbc.Button("Save Details", id='save_ebc', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'})], width=6),
                # button to clear details to allow for new company
                dbc.Col([dbc.Button("Add Additional Company", id='clear_output_ebc', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'})], width=6),
                # dbc.Col(width=6)
            ]),
        ])
    ],
    color="light",
    style={"margin-left": "5rem"}
)

# data table to store details
ebc_table_section = html.Div(
    id='ebc-table-section',
    children=[
        html.P(""),

        html.Div(
            id='ebc_table_details',
            children=[
                html.H4("Data Table", className="card-text", style={'color': kpmgBlue_hash}),

                dash_table.DataTable(
                    id='ebc_table',
                    columns=[{"name": i, "id": i} for i in ebc_df.columns],
                    style_cell={'textAlign': 'left'},
                    style_header={'color': 'white', 'backgroundColor': 'rgb(0,51,141)', 'fontWeight': 'bold'},
                    data=ebc_df.to_dict('records'),
                    export_format="csv",
                    persistence=True,
                    persistence_type='session'
                )

            ], style={'display': 'block'}
        ),
    ],
    style={"margin-left": "5rem"}
)

results_card = html.Div([
    dbc.Card(
        [
            dbc.CardBody([
                html.H5("Exceeding Borrowing Costs"),
                html.P(""),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Calculate", id='ebc-calculate', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}),
                        html.P(""),
                        html.Div(id='ebc-output'),
                        html.P(""),
                    ], width=6),

                    dbc.Col([
                        dbc.Button("Show Workings", id='ebc-workings', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}),
                        html.P(""),
                        html.Div(id='ebc-workings-output'),
                        html.P(""),
                    ], width=6)
                ]),

                html.Hr(style={'height': '2px'}),

                html.H5("Exceeding Borrowing Costs for the de minimis exception"),
                html.P(""),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Calculate", id='ebc-calculate2', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}),
                        html.P(""),
                        html.Div(id='ebc-dm-output')

                    ], width=6),

                    dbc.Col([
                        dbc.Button("Show Workings", id='ebc-dm-workings', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}),
                        html.P(""),
                        html.Div(id='ebc-dm-workings-output'),
                        html.P(""),
                    ], width=6)
                ])

            ])
        ],
        color="light",
        style={"margin-left": "5rem"}
    )
]

)

##------------------------------------------ LAYOUT --------------------------

layout = html.Div([
    card_ebc,
    html.P(""),
    ebc_table_section,
    html.P(""),
    results_card
])


##--------------------------------------------- CALLBACKS ------------------------

# Hide data table until user clicks "See Data"
@dash_app.callback(
    Output(component_id='ebc_table_details', component_property='style'),
    [Input(component_id='save_ebc', component_property='n_clicks')])
def show_hide_element(n_clicks):
    if n_clicks > 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebc_table', 'data'),
    Input('save_ebc', 'n_clicks'),
    State('ebc_table', 'data'),
    State('ebc_table', 'columns'),
    State('group_dd', 'value'),
    State('company_dd', 'value'),
    State('interest_dd', 'value'),
    State('amount_input', 'value'),
    State('tax_dd', 'value'),
    State('legacy_toggle_switch', 'value'),
    State('pbi_input', 'value'),
    State('text_description', 'value')
)
def produce_home_datatable(n_clicks, rows, columns, group_dd, company_dd, interest_dd, amount_input, tax_dd,
                           legacy_toggle_switch, pbi, text):
    if n_clicks > 0:
        forbidden = ["No Groups Entered", "No Companies Entered", "", None]
        forbidden2 = ["", None]
        if group_dd not in forbidden and company_dd not in forbidden:
            if interest_dd not in forbidden2: 
                if interest_dd == 'Interest Expense':
                    if amount_input not in forbidden2 and tax_dd not in forbidden2 and pbi not in forbidden2:
                        if legacy_toggle_switch == False:
                            legacy_value = 'N'
                        elif legacy_toggle_switch == True:
                            legacy_value = 'Y'
                        else:
                            legacy_value= 'N'
                        results_ebc = [group_dd, company_dd, interest_dd, amount_input, tax_dd, legacy_value, pbi, text]
                        # rows.append({ 
                        #     columns[i]['id'] : results_ebc[i] for i in range(0, len(ebc_df.columns)) 
                        # })   
                
                if interest_dd == 'Interest Income':
                    if amount_input not in forbidden2 and tax_dd not in forbidden2 and pbi not in forbidden2:
                        results_ebc = [group_dd, company_dd, interest_dd, amount_input, tax_dd, '', pbi, text]
                        # rows.append({ 
                        #     columns[i]['id'] : results_ebc[i] for i in range(0, len(ebc_df.columns)) 
                        # })   
                
                if interest_dd == 'Interest Spare Capacity':
                    if amount_input not in forbidden2:
                        results_ebc = [group_dd, company_dd, interest_dd, amount_input, '', '', '', text]
                        # rows.append({ 
                        #     columns[i]['id'] : results_ebc[i] for i in range(0, len(ebc_df.columns)) 
                        # })

                rows.append({ 
                     columns[i]['id'] : results_ebc[i] for i in range(0, len(ebc_df.columns)) 
                })              
    return rows


# clearing data for additional companies
@dash_app.callback(
    Output('group_dd', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('company_dd', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('interest_dd', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('amount_input', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('tax_dd', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('legacy_toggle_switch', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False



@dash_app.callback(
    Output('pbi_input', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):

    if n_clicks>0:
        return ''

@dash_app.callback(
    Output('text_description', 'value'),
    Input('clear_output_ebc', 'n_clicks')
)
def clear_output(n_clicks):

    if n_clicks>0:
        return ''
#

@dash_app.callback(Output('ebc-output', 'children'),
              # Output('ebc-calculate', 'n_clicks')],
              Input('ebc-calculate', 'n_clicks'),
              State('ebc_table', 'data')
              )
def ebc_calc(n_clicks, data):
    if n_clicks == 0:
        return "Not yet calculated"
    if n_clicks > 0:
        sum1 = 0
        sum2 = 0
        sum3 = 0
        for row in data:
            if row['Interest Type'] == "Interest Expense":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum1 = float(float(row['Amount (€)'])-pbi_val) * float(row['Tax Rate (%)']) / 12.5
                    sum1 = sum1 + row_sum1
                except ValueError:
                    row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / 12.5
                    sum1 = sum1 + row_sum1

                if row['Legacy Debt'] == 'Y':
                    row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / 12.5
                else:
                    row_sum2 = 0
                sum2 = sum2 + row_sum2

            if row['Interest Type'] == "Interest Income":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum3 = float(float(row['Amount (€)'])-pbi_val) * float(row['Tax Rate (%)']) / 12.5
                    sum3 = sum3 + row_sum3
                except ValueError:
                    row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / 12.5
                    sum3 = sum3 + row_sum3

        tot_sum = sum1 - sum2 - sum3
        formatted_tot_sum = '€{:,.2f}'.format(tot_sum)
        # n_clicks=0
        return formatted_tot_sum  # , n_clicks


@dash_app.callback(Output('ebc-workings-output', 'children'),
              Input('ebc-workings', 'n_clicks'),
              State('ebc_table', 'data')
              )
def ebc_calc(n_clicks, data):
    # if n_clicks == 0:
    #     return "Not yet calculated"
    if n_clicks > 0:
        sum1 = 0
        sum2 = 0
        sum3 = 0
        #pbi_expense_sum = 0
        for row in data:
            if row['Interest Type'] == "Interest Expense":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum1 = float(float(row['Amount (€)'])-pbi_val) * float(row['Tax Rate (%)']) / 12.5
                    sum1 = sum1 + row_sum1
                except ValueError:
                    row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / 12.5
                    sum1 = sum1 + row_sum1
                #row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / 12.5


                if row['Legacy Debt'] == 'Y':
                    row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / 12.5
                else:
                    row_sum2 = 0
                sum2 = sum2 + row_sum2

            if row['Interest Type'] == "Interest Income":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum3 = float(float(row['Amount (€)'])-pbi_val) * float(row['Tax Rate (%)']) / 12.5
                    sum3 = sum3 + row_sum3
                except ValueError:
                    row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / 12.5
                    sum3 = sum3 + row_sum3
                # row_sum3 = float(float(row['Amount (€)']) - float(row['PBI Amount (€)'])) * float(row['Tax Rate (%)']) / 12.5
                # sum3 = sum3 + row_sum3

        tot_sum = sum1 - sum2 - sum3
        formatted_tot_sum = '€{:,.2f}'.format(tot_sum)
        workings = html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div('Interest Expense (ignore PBI): ', style={'font-size': '80%'}),
                    #html.Div('Ignore PBI Amount: '),
                    html.Div('LESS Legacy Debt: ', style={'font-size': '80%'}),
                    html.Div('LESS Interest Income (ignore PBI): ', style={'font-size': '80%'}),
                    #html.Div('Ignore PBI Amount: '),
                    html.Div('')
                ], width=8),
                dbc.Col([
                    html.Div('€{:,.2f}'.format(sum1), style={'text-align':'right', 'font-size': '80%'}),
                    html.Div('-€{:,.2f}'.format(sum2), style={'text-align':'right', 'font-size': '80%'}),
                    html.Div(html.U('-€{:,.2f}'.format(sum3)), style={'text-align':'right', 'font-size': '80%'}),
                    html.Div(html.B('{}'.format(formatted_tot_sum)), style={'text-align':'right', 'font-size': '80%'})
                ], width=3), 
            ])

        ])
        # n_clicks=0
        return workings  # , n_clicks


@dash_app.callback(Output('ebc-dm-output', 'children'),
              Input('ebc-calculate2', 'n_clicks'),
              State('ebc_table', 'data')
              )
def ebc_calc(n_clicks, data):
    if n_clicks == 0:
        return "Not yet calculated"
    if n_clicks > 0:
        sum4 = 0
        sum5 = 0
        sum6 = 0
        for row in data:
            if row['Interest Type'] == "Interest Expense":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum4 = float(float(row['Amount (€)'])-pbi_val) 
                    sum4 = sum4 + row_sum4
                except ValueError:
                    row_sum4 = float(float(row['Amount (€)']))
                    sum4 = sum4 + row_sum4
                # row_sum4 = float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                # sum4 = sum4 + row_sum4
                if row['Legacy Debt'] == 'Y':
                    row_sum5 = float(row['Amount (€)'])
                else:
                    row_sum5 = 0
                sum5 = sum5 + row_sum5
            if row['Interest Type'] == "Interest Income":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum6 = float(float(row['Amount (€)'])-pbi_val) 
                    sum6 = sum6 + row_sum6
                except ValueError:
                    row_sum6 = float(float(row['Amount (€)']))
                    sum6 = sum6 + row_sum6
                # row_sum6 = float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                # sum6 = sum6 + row_sum6
        tot_sum2 = sum4 - sum5 - sum6
        formatted_tot_sum2 = '€{:,.2f}'.format(tot_sum2)
        return formatted_tot_sum2


@dash_app.callback(Output('ebc-dm-workings-output', 'children'),
              Input('ebc-dm-workings', 'n_clicks'),
              State('ebc_table', 'data')
              )
def ebc_calc(n_clicks, data):
    # if n_clicks == 0:
    #     return "Not yet calculated"
    if n_clicks > 0:
        sum4 = 0
        sum5 = 0
        sum6 = 0
        for row in data:
            if row['Interest Type'] == "Interest Expense":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum4 = float(float(row['Amount (€)'])-pbi_val) 
                    sum4 = sum4 + row_sum4
                except ValueError:
                    row_sum4 = float(float(row['Amount (€)']))
                    sum4 = sum4 + row_sum4
                # row_sum4 = float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                # sum4 = sum4 + row_sum4
                if row['Legacy Debt'] == 'Y':
                    row_sum5 = float(row['Amount (€)'])
                else:
                    row_sum5 = 0
                sum5 = sum5 + row_sum5
            if row['Interest Type'] == "Interest Income":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum6 = float(float(row['Amount (€)'])-pbi_val) 
                    sum6 = sum6 + row_sum6
                except ValueError:
                    row_sum6 = float(float(row['Amount (€)']))
                    sum6 = sum6 + row_sum6
        tot_sum2 = sum4 - sum5 - sum6
        formatted_tot_sum2 = '€{:,.2f}'.format(tot_sum2)
        workings = html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div('Interest Expense (Ignore PBI):', style={'font-size': '80%'}),
                    html.Div('LESS Legacy Debt: ', style={'font-size': '80%'}),
                    html.Div('LESS Interest Income (ignore PBI):', style={'font-size': '80%'}),
                    html.Div('')
                ], width=8),
                dbc.Col([
                    html.Div('€{:,.2f}'.format(sum4), style={'text-align':'right', 'font-size': '80%'}),
                    html.Div('-€{:,.2f}'.format(sum5), style={'text-align':'right', 'font-size': '80%'}),
                    html.Div(html.U('-€{:,.2f}'.format(sum6)), style={'text-align':'right', 'font-size': '80%'}),
                    html.Div(html.B('{}'.format(formatted_tot_sum2)), style={'text-align':'right', 'font-size': '80%'})
                ], width=3)
            ])

        ])
        return workings


###---INT CALC STORE---

@dash_app.callback(
    Output('ebc_store_intcalc', 'data'),
    Input('ebc_table', 'data'),
)
def return_ebc(data):
    intcalc = 0
    for row in data:
        if row['Interest Type'] == "Interest Expense":
            if row['Legacy Debt'] == 'Y':
                row_sum = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / 12.5
            else:
                row_sum = 0
            intcalc = intcalc + row_sum
    datalist = [{'intcalc': intcalc}]
    return datalist


###---EBC STORE---

@dash_app.callback(
    Output('ebc_store', 'data'),
    Input('ebc-output', 'children')
)
def return_ebc(ebc):
    data = [{'ebc': ebc}]
    return data


###---EBC DM STORE---

@dash_app.callback(
    Output('ebc_store_dm', 'data'),
    Input('ebc-dm-output', 'children')
)
def return_ebc(ebc_dm):
    data = [{'ebc_dm': ebc_dm}]
    return data


###---SPARE CAPACITY STORE
@dash_app.callback(
    Output('ebc_store_spareCap', 'data'),
    Input('ebc-calculate', 'n_clicks'),
    State('ebc_table', 'data')
)
def return_ebc(data, n_clicks):
    if n_clicks != 0:
        spare_cap = 0
        for row in data:
            if row['Interest Type'] == "Interest Spare Capacity":
                spare_cap = spare_cap + float(row['Amount (€)'])
        datalist = [{'spare_capacity': spare_cap}]

    if n_clicks == 0:
        datalist = [{'spare_capacity': 0}]
    return datalist


##---IMPORT---##

# @app.callback(
#     Output("group_dd", "options"),
#     Input("home_store", "modified_timestamp"),
#     State("home_store", "data"),
# )
# def update_group_dropdown(time_stamp, data):
#         if data != []:
#             group_data = data[0]
#             if group_data['group'] != []:
#                 return [{"label": i, "value": i} for i in group_data['group']]
#             else:
#                 return [{"label": "No Groups", "value": "No Groups"}]
#         else:
#             return [{'label':grp, "value":grp} for grp in group_dummy]

@dash_app.callback(
    Output("group_dd", "options"),
    # Input("home_store", "modified_timestamp"),
    Input("home_store", "data"),
)
def update_group_dropdown(data):
    # group_data = data[0]
    # return [{"label": i, "value": i} for i in group_data['group']]
    if data != [{}]:
        group_data = data[0]
        if group_data['group'] != []:
            return [{"label": i, "value": i} for i in group_data['group']]
        else:
            return [{"label": "No Groups", "value": "No Groups"}]
    else:
        return [{'label': grp, "value": grp} for grp in group_dummy]


@dash_app.callback(
    Output("company_dd", "options"),
    # Input("home_store", "modified_timestamp"),
    Input("home_store", "data"),
)
def update_company_dropdown(data):
    # company_data = data[1]
    # return [{"label": i, "value": i} for i in company_data['company']]

    if data != [{}]:
        company_data = data[1]
        if company_data['company'] != []:
            return [{"label": i, "value": i} for i in company_data['company']]
        else:
            return [{"label": "No Company", "value": "No Company"}]
    else:
        return [{'label': cmp, "value": cmp} for cmp in company_dummy]


# @app.callback(
#     Output("company_dd", "options"),
#     Input("home_store", "modified_timestamp"),
#     State("home_store", "data"),
# )
# def update_company_dropdown(time_stamp, data):
#         if data != []:
#             company_data = data[1]
#             if company_data['company'] != []:
#                 return [{"label": i, "value": i} for i in company_data['company']]
#         else:
#             return [{'label':cmp, "value":cmp} for cmp in company_dummy]


###---TOGGLE COLOUR CALLBACK---
@dash_app.callback(
    Output('legacy_no', 'children'),
    Input('legacy_toggle_switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('legacy_yes', 'children'),
    Input('legacy_toggle_switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})