import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
import numpy as np

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.ZEPHYR])

kpmgBlue_hash = '#00338D'

# If yes, add the results of all companies that have selected yes together. Any company with No, keep separate.
# yes_df = pd.read_csv("yes_table.csv")
# yes_df.columns = ['Group Name', 'Company Name', 'Company?', 'Corporation Tax Chargeable?', 'Standalone Entity?', 'In Interest Group?']

home_df = pd.DataFrame(columns=['Group', 'Company', 'In Interest Group?'])

##------------------------------HOME_CARDS------------------------------------------------------
# CREATING CARD WHERE USER INPUTS DETAILS
card_question = dbc.Card(
    [
        dbc.CardBody([

            # title of card
            dbc.Row([
                dbc.Col([html.H2("Initial Setup", className="card-title", style={'color': kpmgBlue_hash})], width=10),
                dbc.Col([
                    html.Div(
                        dbc.Button('Next Page', href='/exceeding-borrowing-costs',
                                   style={'backgroundColor': '#3459e6', 'border-color': '#FFFFFF'})
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
            # html.Hr(style={'height': '2px'}),

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
                dbc.Col(dbc.Button("Add Details", id='save_home', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}), width=6),
                dbc.Col(dbc.Button("Add Additional Company", id='clear_output', n_clicks=0,
                                   style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}), width=6),
            #     dbc.Col(dbc.Button("Save", id='save_output', n_clicks=0,
            #                        style={'backgroundColor': kpmgBlue_hash, 'width': '100%'}), width=4)
            ]),

            # dbc.Button("Save Details", id='save_home', n_clicks=0, style={'backgroundColor': kpmgBlue_hash}),

            # html.P(""),

            # dbc.Button("Add Additional Company", id='clear_output', n_clicks=0, style={'backgroundColor': kpmgBlue_hash}),

            # Table - If yes, add the results of all companies that have selected yes together. Any company with No, keep separate.
            # html.Div(

            #     id='datatable-container',
            #     children = [
            #     html.Button('Update Table', id='update-yestable-button', n_clicks=0),
            #     html.P(""),

            #     dash_table.DataTable(
            #         id='home_table_ig',
            #         columns=[{"name": i, "id": i} for i in yes_df.columns],
            #         style_cell={'textAlign':'left'},
            #         style_header={'color':'white', 'backgroundColor':'rgb(0,51,141)', 'fontWeight':'bold'},
            #         data=yes_df.to_dict('records')
            #         )
            #     ],
            #     style = {'display': 'block'}
            # ),
        ])
    ],
    color="light",
    style={"margin-left": "5rem"}
)

# Data Table to store details of Initial Setup
home_table_section = html.Div(
    id='home-table-section',
    children=[
        # dbc.Button("See Data", id='df-button1', n_clicks=0, style={'backgroundColor': kpmgBlue_hash}),

        html.P(""),

        html.Div(
            id='home_table_details',
            children=[
                html.H4("Data Table", className="card-text", style={'color': kpmgBlue_hash}),

                dash_table.DataTable(
                    id='home_table',
                    columns=[{"name": i, "id": i} for i in home_df.columns],
                    style_cell={'textAlign': 'left', 'height': 'auto', 'minWidth': '120px', 'width': '120px',
                                'maxWidth': '120px'},
                    style_header={'color': 'white', 'backgroundColor': 'rgb(0,51,141)', 'fontWeight': 'bold'},
                    data=home_df.to_dict('records'),
                    export_format="csv",
                    persistence=True,
                    persistence_type='session'
                )

            ], style={'display': 'block'}
        ),
    ],
    style={"margin-left": "5rem"}
)

##---------------------------LAYOUT-----------------------------------------------------------


layout = html.Div([
    card_question,
    html.P(""),
    home_table_section,
    # dcc.Link('Next', href='/exceeding-borrowing-costs', style={'color': kpmgBlue_hash, "position": "relative", "bottom": -10,
    # "right": -1030})
])


##--------------------------HOME CALLBACKS------------------------------------------------


# Hide data table until user clicks see data
@app.callback(
    Output(component_id='home_table_details', component_property='style'),
    [Input(component_id='save_home', component_property='n_clicks')])
def show_hide_element(n_clicks):
    if n_clicks > 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


def within_scope(company, chargeable, standalone):
    if company == True and chargeable == True and standalone != True:
        return True
    else:
        return False
    # if company== True:
    #     A= True
    # elif company == False:
    #     A=False
    # else:
    #     A=False

    # if chargeable== True:
    #     B= True
    # elif chargeable == False:
    #     B=False
    # else:
    #     B=False

    # if standalone== False:
    #     C= False
    # elif standalone == True:
    #     C= True
    # else:
    #     C= True

    # if [A,B,C] == [True, True, False]:
    #     return True
    # else:
    #     return False



# Update table when user clicks Save Data
@app.callback(
    Output('home_table', 'data'),
    Input('save_home', 'n_clicks'),
    State('home_table', 'data'),
    State('home_table', 'columns'),
    State('group', 'value'),
    State('company', 'value'),
    State('interest-group-toggle-switch', 'value'),
    State('company-toggle-switch', 'value'),
    State('chargeable-toggle-switch', 'value'),
    State('standalone-toggle-switch', 'value')
)
def produce_home_datatable(n_clicks, rows, columns, group, company, interest_group, company_toggle, chargeable_toggle, standalone_toggle):
    if n_clicks > 0:
        forbidden = [None, ""]
        if group not in forbidden and company not in forbidden:
            if within_scope(company_toggle, chargeable_toggle, standalone_toggle) == True:
                if interest_group == False:
                    interest_group_value = 'N'
                elif interest_group == True:
                    interest_group_value = 'Y'
                else:
                    interest_group_value = 'N'
                results_home = [group, company, interest_group_value]
                print(results_home)
                rows.append({
                    columns[i]['id']: results_home[i] for i in range(0, len(home_df.columns))
                })
    return rows


# clearing data for additional companies
@app.callback(
    Output('group', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@app.callback(
    Output('company', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@app.callback(
    Output('company-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


@app.callback(
    Output('chargeable-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


@app.callback(
    Output('standalone-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


@app.callback(
    Output('interest-group-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


@app.callback(
    Output('outside_scope_company', 'style'),
    Input('company-toggle-switch', 'value')
)
def show_hide_element(visibility_state):
    if visibility_state == False:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
    elif visibility_state == True:
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}


@app.callback(
    Output('outside_scope_chargeable', 'style'),
    Input('chargeable-toggle-switch', 'value')
)
def show_hide_element(visibility_state):
    if visibility_state == False:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
    elif visibility_state == True:
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}


@app.callback(
    Output('outside_scope_standalone', 'style'),
    Input('standalone-toggle-switch', 'value')
)
def show_hide_element(visibility_state):
    if visibility_state == True:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
    elif visibility_state == False:
        return {'display': 'none'}
    else:
        return {'display': 'none'}







###---TOGGLE SWITCH COLOUR CALLBACKS---

# To make option selected by toggle switch bold and blue

@app.callback(
    Output('ig_no', 'children'),
    Input('interest-group-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@app.callback(
    Output('ig_yes', 'children'),
    Input('interest-group-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


@app.callback(
    Output('standalone_no', 'children'),
    Input('standalone-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@app.callback(
    Output('standalone_yes', 'children'),
    Input('standalone-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


@app.callback(
    Output('chargeable_no', 'children'),
    Input('chargeable-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@app.callback(
    Output('chargeable_yes', 'children'),
    Input('chargeable-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


@app.callback(
    Output('company_no', 'children'),
    Input('company-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@app.callback(
    Output('company_yes', 'children'),
    Input('company-toggle-switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


# @app.callback(
#     Output('home_store', 'data'),
#     State('home_table', 'data'),
#     Input('save_output', 'n_clicks'),
#     State('save_home', 'n_clicks')
# )
# def results_export(data, n_clicks, details_entered):
#     # before save has been clicked
#     if n_clicks == 0:
#         return [{'group': ['No Groups Saved']}, {'company': ['No Companies Saved']}]

#     # save has been clicked
#     if n_clicks > 0:

#         # no details have been added to table
#         if details_entered == 0:
#             return [{'group': ['Must Save Details']}, {'company': ['Must Save Details']}]

#         # there are companies/groups to be saved
#         elif details_entered > 0:
#             data_list = []
#             i = 0
#             num_rows = len(data)
#             group_list = [None] * num_rows
#             company_list = [None] * num_rows
#             for row in data:
#                 group_list[i] = row['Group']
#                 company_list[i] = row['Company']
#                 i = i + 1
#             # removing duplicate group/company entries
#             group_list = list(set(group_list))
#             company_list = list(set(company_list))
#             data_list = [{'group': group_list}, {'company': company_list}]
#             print(data_list)
#             return data_list


@app.callback(
    Output('home_store', 'data'),
    Input('home_table', 'data'),
    #Input('save_output', 'n_clicks'),
    #State('save_home', 'n_clicks')
)
def results_export(data):
    num_rows = len(data)
    if num_rows == 0:
    # # no details have been added to table
    #     if details_entered == 0:
        return [{'group': ['No Groups Entered']}, {'company': ['No Companies Entered']}]
    else:
        # there are companies/groups to be saved
        # elif details_entered > 0:
        data_list = []
        i = 0
        group_list = [None] * num_rows
        company_list = [None] * num_rows
        for row in data:
            group_list[i] = row['Group']
            company_list[i] = row['Company']
            i = i + 1
            # removing duplicate group/company entries
        group_list = list(set(group_list))
        company_list = list(set(company_list))
        data_list = [{'group': group_list}, {'company': company_list}]
        print(data_list)
        return data_list
