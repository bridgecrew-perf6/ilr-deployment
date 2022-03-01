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


##-------------------------------HOME CALLBACKS--------------------------------


# @dash_app.callback(
#     Output(component_id='home_table_details', component_property='style'),
#     Input(component_id='clear_output', component_property='n_clicks'))
# def show_hide_element(n_clicks):
#     if n_clicks > 0:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}


# def within_scope(company, chargeable, standalone):
#     if company == True and chargeable == True and standalone != True:
#         return True
#     else:
#         return False


# @dash_app.callback(
#     Output('home_table', 'data'),
#     Input('clear_output', 'n_clicks'),
#     State('home_table', 'data'),
#     State('home_table', 'columns'),
#     State('group', 'value'),
#     State('company', 'value'),
#     State('interest-group-toggle-switch', 'value'),
#     State('company-toggle-switch', 'value'),
#     State('chargeable-toggle-switch', 'value'),
#     State('standalone-toggle-switch', 'value'),
#     State('home_table_store', 'data')
# )
# def produce_home_datatable(n_clicks, rows, columns, group, company, interest_group, company_toggle, chargeable_toggle,
#                            standalone_toggle, store):
#     if n_clicks == 0:
#         if store == [{}] or store is None:
#             return []
#         elif store != [{}]:
#             home_table = store[0]
#             home_table_data = home_table['home_table_data']
#             home_table_df = pd.DataFrame(home_table_data)
#             data_ = home_table_df.to_dict('records')
#             return data_

#     if n_clicks != 0:
#         forbidden = [None, ""]
#         if group not in forbidden and company not in forbidden:
#             if within_scope(company_toggle, chargeable_toggle, standalone_toggle):
#                 if not interest_group:
#                     interest_group_value = 'N'
#                 elif interest_group:
#                     interest_group_value = 'Y'
#                 else:
#                     interest_group_value = 'N'
#                 results_home = [group, company, interest_group_value]
#                 rows.append({
#                     columns[i]['id']: results_home[i] for i in range(0, len(home_df.columns))
#                 })
#     return rows


# ##-------Update Initial Store Values--------
# # store datatable values

# @dash_app.callback(
#     Output('home_table_store', 'data'),
#     Input('home_table', 'data'),
#     Input('home_table', 'columns')
# )
# def return_home(data, columns):
#     num_rows = len(data)
#     groups = [''] * num_rows
#     companies = [''] * num_rows
#     interest_group = [''] * num_rows

#     for (i, row) in zip(range(0, num_rows), data):
#         groups[i] = row['Group']
#         companies[i] = row['Company']
#         interest_group[i] = row['In Interest Group?']
#     store_data = {'Group': groups, 'Company': companies, 'In Interest Group?': interest_group}
#     datalist = [{'home_table_data': store_data}]

#     return datalist


# ##----- spot rate callback ---------------------

# @dash_app.callback(
#     Output('spot_rate_input', 'style'),
#     Input('currency_dd', 'value')
# )
# def show_hide_element(currency):
#     if currency == 'USD ($)':
#         return {'display': 'block', 'width': '80%'}
#     elif currency == 'GBP (£)':
#         return {'display': 'block', 'width': '80%'}
#     elif currency == 'Other':
#         return {'display': 'block', 'width': '80%'}
#     elif currency == 'Euro (€)':
#         return {'display': 'none'}
#     else:
#         return {'display': 'none'}


# @dash_app.callback(
#     Output('spot_rate_store', 'data'),
#     Input('currency_dd', 'value'),
#     Input('spot_rate_input', 'value')
# )
# def spot_rate(currency, spot_rate):
#     if currency == 'Euro (€)' or currency == '' or currency is None:
#         store_data = {'currency': 'Euro (€)', 'spot_rate': "No Spot Rate"}
#     else:
#         if spot_rate == '' or spot_rate is None:
#             store_data = {'currency': currency, 'spot_rate': "No Spot Rate Entered"}
#         else:
#             store_data = {'currency': currency, 'spot_rate': spot_rate}
#     datalist = [store_data]
#     return datalist


# ##----CLEARING FIELDS FOR ADDITIONAL COMPANIES-------

# @dash_app.callback(
#     Output('group', 'value'),
#     Input('clear_output', 'n_clicks')
# )
# def clear_output(n_clicks):
#     if n_clicks > 0:
#         return ''


# @dash_app.callback(
#     Output('company', 'value'),
#     Input('clear_output', 'n_clicks')
# )
# def clear_output(n_clicks):
#     if n_clicks > 0:
#         return ''


# @dash_app.callback(
#     Output('company-toggle-switch', 'value'),
#     Input('clear_output', 'n_clicks')
# )
# def clear_output(n_clicks):
#     if n_clicks > 0:
#         return False


# @dash_app.callback(
#     Output('chargeable-toggle-switch', 'value'),
#     Input('clear_output', 'n_clicks')
# )
# def clear_output(n_clicks):
#     if n_clicks > 0:
#         return False


# @dash_app.callback(
#     Output('standalone-toggle-switch', 'value'),
#     Input('clear_output', 'n_clicks')
# )
# def clear_output(n_clicks):
#     if n_clicks > 0:
#         return False


# @dash_app.callback(
#     Output('interest-group-toggle-switch', 'value'),
#     Input('clear_output', 'n_clicks')
# )
# def clear_output(n_clicks):
#     if n_clicks > 0:
#         return False


# ##-----------OUTSIDE SCOPE CALLBACKS----------

# @dash_app.callback(
#     Output('outside_scope_company', 'style'),
#     Input('company-toggle-switch', 'value')
# )
# def show_hide_element(visibility_state):
#     if not visibility_state:
#         return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
#     elif visibility_state:
#         return {'display': 'none'}
#     else:
#         return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}


# @dash_app.callback(
#     Output('outside_scope_chargeable', 'style'),
#     Input('chargeable-toggle-switch', 'value')
# )
# def show_hide_element(visibility_state):
#     if not visibility_state:
#         return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
#     elif visibility_state:
#         return {'display': 'none'}
#     else:
#         return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}


# @dash_app.callback(
#     Output('outside_scope_standalone', 'style'),
#     Input('standalone-toggle-switch', 'value')
# )
# def show_hide_element(visibility_state):
#     if visibility_state:
#         return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
#     elif not visibility_state:
#         return {'display': 'none'}
#     else:
#         return {'display': 'none'}


# ###---TOGGLE SWITCH COLOUR CALLBACKS---
# # To make option selected by toggle switch bold and blue

# @dash_app.callback(
#     Output('ig_no', 'children'),
#     Input('interest-group-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6("No", style={'color': '#D4D4D4'})
#     else:
#         return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


# @dash_app.callback(
#     Output('ig_yes', 'children'),
#     Input('interest-group-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
#     else:
#         return html.H6("Yes", style={'color': '#D4D4D4'})


# @dash_app.callback(
#     Output('standalone_no', 'children'),
#     Input('standalone-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6("No", style={'color': '#D4D4D4'})
#     else:
#         return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


# @dash_app.callback(
#     Output('standalone_yes', 'children'),
#     Input('standalone-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
#     else:
#         return html.H6("Yes", style={'color': '#D4D4D4'})


# @dash_app.callback(
#     Output('chargeable_no', 'children'),
#     Input('chargeable-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6("No", style={'color': '#D4D4D4'})
#     else:
#         return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


# @dash_app.callback(
#     Output('chargeable_yes', 'children'),
#     Input('chargeable-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
#     else:
#         return html.H6("Yes", style={'color': '#D4D4D4'})


# @dash_app.callback(
#     Output('company_no', 'children'),
#     Input('company-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6("No", style={'color': '#D4D4D4'})
#     else:
#         return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


# @dash_app.callback(
#     Output('company_yes', 'children'),
#     Input('company-toggle-switch', 'value')
# )
# def bold(switch):
#     if switch:
#         return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
#     else:
#         return html.H6("Yes", style={'color': '#D4D4D4'})


# ##--------------HOME STORE CALLBACKS-------

# @dash_app.callback(
#     Output('home_store', 'data'),
#     Input('home_table', 'data')
# )
# def results_export(data):
#     num_rows = len(data)
#     if num_rows == 0:
#         ## no details have been added to table
#         return [{'group': ['No Groups Entered']}, {'company': ['No Companies Entered']}]
#     else:
#         # there are companies/groups to be saved
#         data_list = []
#         group_list = [None] * num_rows
#         company_list = [None] * num_rows
#         for (i, row) in zip(range(0, num_rows), data):
#             group_list[i] = row['Group']
#             company_list[i] = row['Company']
#         # removing duplicate group/company entries
#         group_list = sorted(list(set(group_list)))
#         company_list = sorted(list(set(company_list)))
#         data_list = [{'group': group_list}, {'company': company_list}]
#         return data_list
