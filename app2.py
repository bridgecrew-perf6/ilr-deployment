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

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##---------------------------OVERALL LAYOUT------------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# sidebar properties
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "17rem",
    "padding": "2rem 1rem",
    "background-color": kpmgBlue_hash,
    "color": "#FFFFFF"
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# creating side bar
sidebar = html.Div(
    [
        # kpmg logo
        dbc.Row([
            dbc.Col(
                html.Div(html.Img(src="assets/kpmg_logo.png", height="100px"), style={'text-align': 'center'})
            )]),

        # navigation links to different pages
        dbc.Row(
            [
                # title and subtitle
                html.Div(html.H2("ILR Tax Model", style={"color": "#FFFFFF"}), style={'text-align': 'center'}),
                html.Hr(),
                # setting up page contents
                dbc.Nav(
                    [
                        dbc.NavLink("Initial Setup", href="/home", style={"color": "#FFFFFF"}, active="exact"),
                        dbc.NavLink("Exceeding Borrowing Costs", href="/exceeding-borrowing-costs",
                                    style={"color": "#FFFFFF"}, active="exact"),
                        dbc.NavLink("Tax EBITDA", href="/tax-ebitda", style={"color": "#FFFFFF"}, active="exact"),
                        dbc.NavLink("Group Ratio", href="/group-ratio", style={"color": "#FFFFFF"}, active="exact"),
                        dbc.NavLink("Equity Ratio", href="/equity-ratio", style={"color": "#FFFFFF"}, active="exact"),
                        dbc.NavLink("Disallowance Formula", href="/disallowance-formula", style={"color": "#FFFFFF"},
                                    active="exact"),
                        dbc.NavLink("Summary", href="/summary", style={"color": "#FFFFFF"}, active="exact"),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ])
    ],
    style=SIDEBAR_STYLE
)

# we define in a call back what each "page-content" is referring to
content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    content,

    ##---MEMORY STORES---

    # Store component for tabs
    dcc.Store(id='login_store', data=[{}], storage_type="session"),
    dcc.Store(id='home_store', data=[{}], storage_type="session"),
    dcc.Store(id='home_table_store', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store_dm', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_table_store', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store_intcalc', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store_spareCap', data=[{}], storage_type="session"),
    dcc.Store(id='tax_ebitda_store', data=[{}], storage_type="session"),
    dcc.Store(id='tax_ebitda_store_lim_spare_cap', data=[{}], storage_type="session"),
    dcc.Store(id='group_ratio_store', data=[{}], storage_type="session"),
    dcc.Store(id='equity_ratio_store_group', data=[{}], storage_type="session"),
    dcc.Store(id='equity_ratio_store_worldwide', data=[{}], storage_type="session"),
    dcc.Store(id='disallowance_store', data=[{}], storage_type="session"),
    dcc.Store(id='ebitda_table_store', data=[{}], storage_type="session"),
    dcc.Store(id='spot_rate_store', data=[{}], storage_type="session")
])

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------LOGIN PAGE-------------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##------------------------------LOGIN LAYOUT------------------------------------

index_page = html.Div(
    [
        dbc.Button("Open modal", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Login"), close_button=False),
                dbc.ModalBody(
                    html.Div([
                        html.Div(
                            dcc.Input(id="user", type="text", placeholder="Enter Username", className="inputbox1",
                                      style={'margin-left': '35%', 'width': '450px', 'height': '45px',
                                             'padding': '10px', 'margin-top': '60px',
                                             'font-size': '16px', 'border-width': '3px', 'border-color': '#a0a3a2'
                                             }),
                        ),
                        html.Div(
                            dcc.Input(id="passw", type="password", placeholder="Enter Password", className="inputbox2",
                                      style={'margin-left': '35%', 'width': '450px', 'height': '45px',
                                             'padding': '10px', 'margin-top': '10px',
                                             'font-size': '16px', 'border-width': '3px', 'border-color': '#a0a3a2',
                                             }),
                        ),
                        html.Div(
                            dbc.Button('Verify', id='verify', n_clicks=0,
                                       style={'border-width': '3px', 'font-size': '14px',
                                              'backgroundColor': kpmgBlue_hash, 'border-color': '#FFFFFF'}),
                            style={'margin-left': '45%', 'padding-top': '30px'}),
                        html.Div(id='output1')
                    ])
                ),
            ],
            id="modal",
            fullscreen=True,
            is_open=True,
        ),
    ]
)


@dash_app.callback(
    [Output('output1', 'children'),
     Output('login_store', 'data')],
    Input('verify', 'n_clicks'),
    State('user', 'value'),
    State('passw', 'value')
)
def update_output(n_clicks, uname, passw):
    li = {'tax': 'tax123'}

    if uname == '' or uname == None or passw == '' or passw == None:
        login_details = [{}]
        return html.Div(children='', style={'padding-left': '550px', 'padding-top': '10px'}), login_details
    if uname not in li:
        login_details = [{}]
        return html.Div(children='Incorrect Username or Password.',
                        style={'margin-left': '35%', 'padding': '10px', 'padding-top': '40px',
                               'font-size': '16px'}), login_details
    if li[uname] == passw:
        login_details = [{'uname': 'tax', 'passw': 'tax123'}]
        return html.Div(dcc.Link('Access Granted!', href='/home',
                                 style={'color': '#183d22', 'font-weight': 'bold', "text-decoration": "none",
                                        'font-size': '20px'}),
                        style={'margin-left': '35%', 'padding': '10px', 'padding-top': '40px', 'font-size': '16px',
                               'padding-top': '40px'}), login_details
    else:
        login_details = [{}]
        return html.Div(children='Incorrect Username or Password.',
                        style={'margin-left': '35%', 'padding': '10px', 'padding-top': '40px',
                               'font-size': '16px'}), login_details


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------HOME PAGE-------------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


##------------------------------HOME LAYOUT------------------------------------

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

home_layout = html.Div([
    home_card_question,
    html.P(""),
    home_table_section,
])


##-------------------------------HOME CALLBACKS--------------------------------


@dash_app.callback(
    Output(component_id='home_table_details', component_property='style'),
    Input(component_id='clear_output', component_property='n_clicks'))
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


@dash_app.callback(
    Output('home_table', 'data'),
    Input('clear_output', 'n_clicks'),
    State('home_table', 'data'),
    State('home_table', 'columns'),
    State('group', 'value'),
    State('company', 'value'),
    State('interest-group-toggle-switch', 'value'),
    State('company-toggle-switch', 'value'),
    State('chargeable-toggle-switch', 'value'),
    State('standalone-toggle-switch', 'value'),
    State('home_table_store', 'data')
)
def produce_home_datatable(n_clicks, rows, columns, group, company, interest_group, company_toggle, chargeable_toggle,
                           standalone_toggle, store):
    if n_clicks == 0:
        if store == [{}] or store is None:
            return []
        elif store != [{}]:
            home_table = store[0]
            home_table_data = home_table['home_table_data']
            home_table_df = pd.DataFrame(home_table_data)
            data_ = home_table_df.to_dict('records')
            return data_

    if n_clicks != 0:
        forbidden = [None, ""]
        if group not in forbidden and company not in forbidden:
            if within_scope(company_toggle, chargeable_toggle, standalone_toggle):
                if not interest_group:
                    interest_group_value = 'N'
                elif interest_group:
                    interest_group_value = 'Y'
                else:
                    interest_group_value = 'N'
                results_home = [group, company, interest_group_value]
                rows.append({
                    columns[i]['id']: results_home[i] for i in range(0, len(home_df.columns))
                })
    return rows


##-------Update Initial Store Values--------
# store datatable values

@dash_app.callback(
    Output('home_table_store', 'data'),
    Input('home_table', 'data'),
    Input('home_table', 'columns')
)
def return_home(data, columns):
    num_rows = len(data)
    groups = [''] * num_rows
    companies = [''] * num_rows
    interest_group = [''] * num_rows

    for (i, row) in zip(range(0, num_rows), data):
        groups[i] = row['Group']
        companies[i] = row['Company']
        interest_group[i] = row['In Interest Group?']
    store_data = {'Group': groups, 'Company': companies, 'In Interest Group?': interest_group}
    datalist = [{'home_table_data': store_data}]

    return datalist


##----- spot rate callback ---------------------

@dash_app.callback(
    Output('spot_rate_input', 'style'),
    Input('currency_dd', 'value')
)
def show_hide_element(currency):
    if currency == 'USD ($)':
        return {'display': 'block', 'width': '80%'}
    elif currency == 'GBP (£)':
        return {'display': 'block', 'width': '80%'}
    elif currency == 'Other':
        return {'display': 'block', 'width': '80%'}
    elif currency == 'Euro (€)':
        return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('spot_rate_store', 'data'),
    Input('currency_dd', 'value'),
    Input('spot_rate_input', 'value')
)
def spot_rate(currency, spot_rate):
    if currency == 'Euro (€)' or currency == '' or currency is None:
        store_data = {'currency': 'Euro (€)', 'spot_rate': "No Spot Rate"}
    else:
        if spot_rate == '' or spot_rate is None:
            store_data = {'currency': currency, 'spot_rate': "No Spot Rate Entered"}
        else:
            store_data = {'currency': currency, 'spot_rate': spot_rate}
    datalist = [store_data]
    return datalist


##----CLEARING FIELDS FOR ADDITIONAL COMPANIES-------

@dash_app.callback(
    Output('group', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('company', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('company-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


@dash_app.callback(
    Output('chargeable-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


@dash_app.callback(
    Output('standalone-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


@dash_app.callback(
    Output('interest-group-toggle-switch', 'value'),
    Input('clear_output', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


##-----------OUTSIDE SCOPE CALLBACKS----------

@dash_app.callback(
    Output('outside_scope_company', 'style'),
    Input('company-toggle-switch', 'value')
)
def show_hide_element(visibility_state):
    if not visibility_state:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
    elif visibility_state:
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}


@dash_app.callback(
    Output('outside_scope_chargeable', 'style'),
    Input('chargeable-toggle-switch', 'value')
)
def show_hide_element(visibility_state):
    if not visibility_state:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
    elif visibility_state:
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}


@dash_app.callback(
    Output('outside_scope_standalone', 'style'),
    Input('standalone-toggle-switch', 'value')
)
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '5vw', 'margin-top': '1vw'}
    elif not visibility_state:
        return {'display': 'none'}
    else:
        return {'display': 'none'}


###---TOGGLE SWITCH COLOUR CALLBACKS---
# To make option selected by toggle switch bold and blue

@dash_app.callback(
    Output('ig_no', 'children'),
    Input('interest-group-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('ig_yes', 'children'),
    Input('interest-group-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


@dash_app.callback(
    Output('standalone_no', 'children'),
    Input('standalone-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('standalone_yes', 'children'),
    Input('standalone-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


@dash_app.callback(
    Output('chargeable_no', 'children'),
    Input('chargeable-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('chargeable_yes', 'children'),
    Input('chargeable-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


@dash_app.callback(
    Output('company_no', 'children'),
    Input('company-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('company_yes', 'children'),
    Input('company-toggle-switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


##--------------HOME STORE CALLBACKS-------

@dash_app.callback(
    Output('home_store', 'data'),
    Input('home_table', 'data')
)
def results_export(data):
    num_rows = len(data)
    if num_rows == 0:
        ## no details have been added to table
        return [{'group': ['No Groups Entered']}, {'company': ['No Companies Entered']}]
    else:
        # there are companies/groups to be saved
        data_list = []
        group_list = [None] * num_rows
        company_list = [None] * num_rows
        for (i, row) in zip(range(0, num_rows), data):
            group_list[i] = row['Group']
            company_list[i] = row['Company']
        # removing duplicate group/company entries
        group_list = sorted(list(set(group_list)))
        company_list = sorted(list(set(company_list)))
        data_list = [{'group': group_list}, {'company': company_list}]
        return data_list


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------EBC PAGE-------------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##-------------------------------EBC VARIABLES--------------------------------

group_dummy = ["N/A"]
company_dummy = ["N/A"]
interest_group_dummy = ["Interest Expense", "Interest Income", "Interest Spare Capacity"]
tax_rates = [12.5, 25, 33]
currencies = ['Euro (€)', 'USD ($)']
column_names = ['Group', 'Company', 'Interest Type', 'Amount (€)', 'Tax Rate (%)', 'Legacy Debt',
                'PBI Amount (€)', 'Text Description']
ebc_df = pd.DataFrame(columns=column_names)
# ebc_df = pd.DataFrame(data)

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

ebc_layout = html.Div([
    card_ebc,
    html.P(""),
    ebc_table_section,
    html.P(""),
    ebc_results_table_section,
    html.P(""),
    ebc_workings_card
])


##-------------------------------EBC CALLBACKS--------------------------------
# Hide PBI until user clicks "Yes"
@dash_app.callback(
    Output(component_id='ebc_pbi_input', component_property='style'),
    [Input(component_id='ebc_pbi_toggle_switch', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state == True:
        return {'display': 'block', 'width': '80%'}
    if visibility_state == False:
        return {'display': 'none'}
    else:
        return {'display': 'none'}


##---------SHOW DATATABLE CALLBACK------
# Hide data table until user clicks "See Data"
@dash_app.callback(
    Output(component_id='ebc_table_details', component_property='style'),
    [Input(component_id='save_ebc', component_property='n_clicks')])
def show_hide_element(n_clicks):
    if n_clicks > 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


##--------UPDATE DATATABLE CALLBACK-------

@dash_app.callback(
    Output('ebc_table', 'data'),
    Input('save_ebc', 'n_clicks'),
    State('ebc_table', 'data'),
    State('ebc_table', 'columns'),
    State('ebc_group_dd', 'value'),
    State('ebc_company_dd', 'value'),
    State('ebc_interest_dd', 'value'),
    State('ebc_amount_input', 'value'),
    State('ebc_tax_dd', 'value'),
    State('ebc_legacy_toggle_switch', 'value'),
    State('ebc_pbi_input', 'value'),
    State('ebc_text_description', 'value'),
    State('ebc_table_store', 'data'),
    State('spot_rate_store', 'data'),
    State('ebc_amount_in_euro_value', 'children'),
    State('ebc_pbi_amount_in_euro_value', 'children'),

)
def produce_home_datatable(n_clicks, rows, columns, group_dd, company_dd, interest_dd, amount_input, tax_dd,
                           legacy_toggle_switch, pbi, text, store, spot_rate_store, euro_amount, euro_pbi):
    if n_clicks == 0:
        if store == [{}] or store == None:
            return []
        elif store != [{}]:
            ebc_table = store[0]
            ebc_table_data = ebc_table['ebc_table_data']
            ebc_table_df = pd.DataFrame(ebc_table_data)

            data = ebc_table_df.to_dict('records')
            return data
    if n_clicks > 0:
        forbidden = ["No Groups Entered", "No Companies Entered", "", None]
        forbidden2 = ["", None]
        if group_dd not in forbidden and company_dd not in forbidden:
            if interest_dd not in forbidden2:
                details = spot_rate_store[0]
                currency = details['currency']
                if currency == 'Euro (€)':
                    if interest_dd == 'Interest Expense':
                        if amount_input not in forbidden2 and tax_dd not in forbidden2 and pbi not in forbidden2:
                            if not legacy_toggle_switch:
                                legacy_value = 'N'
                            elif legacy_toggle_switch:
                                legacy_value = 'Y'
                            else:
                                legacy_value = 'N'
                            results_ebc = [group_dd, company_dd, interest_dd, amount_input, tax_dd, legacy_value, pbi,
                                           text]

                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })
                        if amount_input not in forbidden2 and tax_dd not in forbidden2 and pbi in forbidden2:
                            if not legacy_toggle_switch:
                                legacy_value = 'N'
                            elif legacy_toggle_switch:
                                legacy_value = 'Y'
                            else:
                                legacy_value = 'N'
                            results_ebc = [group_dd, company_dd, interest_dd, amount_input, tax_dd, legacy_value, 0,
                                           text]

                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })

                    if interest_dd == 'Interest Income':
                        if amount_input not in forbidden2 and tax_dd not in forbidden2 and pbi not in forbidden2:
                            results_ebc = [group_dd, company_dd, interest_dd, amount_input, tax_dd, '', pbi, text]
                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })
                        if amount_input not in forbidden2 and tax_dd not in forbidden2 and pbi in forbidden2:
                            results_ebc = [group_dd, company_dd, interest_dd, amount_input, tax_dd, '', 0, text]
                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })

                    if interest_dd == 'Interest Spare Capacity':
                        if amount_input not in forbidden2:
                            results_ebc = [group_dd, company_dd, interest_dd, amount_input, '', '', '', text]

                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })

                else:
                    if interest_dd == 'Interest Expense':
                        if euro_amount not in forbidden2 and tax_dd not in forbidden2 and euro_pbi not in forbidden2:
                            if not legacy_toggle_switch:
                                legacy_value = 'N'
                            elif legacy_toggle_switch:
                                legacy_value = 'Y'
                            else:
                                legacy_value = 'N'
                            results_ebc = [group_dd, company_dd, interest_dd, '{:,.2f}'.format(float(euro_amount)), tax_dd, legacy_value,
                                            '{:,.2f}'.format(float(euro_pbi)), text]

                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })

                        if euro_amount not in forbidden2 and tax_dd not in forbidden2 and euro_pbi in forbidden2:
                            if not legacy_toggle_switch:
                                legacy_value = 'N'
                            elif legacy_toggle_switch:
                                legacy_value = 'Y'
                            else:
                                legacy_value = 'N'
                            results_ebc = [group_dd, company_dd, interest_dd, '{:,.2f}'.format(float(euro_amount)), tax_dd, legacy_value,
                                           0, text]

                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })

                    if interest_dd == 'Interest Income':
                        if euro_amount not in forbidden2 and tax_dd not in forbidden2 and euro_pbi not in forbidden2:
                            results_ebc = [group_dd, company_dd, interest_dd, '{:,.2f}'.format(float(euro_amount)), tax_dd, '',
                                           '{:,.2f}'.format(float(euro_pbi)), text]
                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })
                        if euro_amount not in forbidden2 and tax_dd not in forbidden2 and euro_pbi in forbidden2:
                            results_ebc = [group_dd, company_dd, interest_dd,  '{:,.2f}'.format(float(euro_amount)), tax_dd, '', 0, text]
                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })

                    if interest_dd == 'Interest Spare Capacity':
                        if euro_amount not in forbidden2:
                            results_ebc = [group_dd, company_dd, interest_dd, '{:,.2f}'.format(float(euro_amount)), '', '', '', text]

                            rows.append({
                                columns[i]['id']: results_ebc[i] for i in range(0, len(ebc_df.columns))
                            })
        return rows


# store datatable values
@dash_app.callback(
    Output('ebc_table_store', 'data'),
    Input('ebc_table', 'data'),
    Input('ebc_table', 'columns')
)
def return_ebc(data, columns):
    groups = [''] * len(data)
    companies = [''] * len(data)
    interest_types = [''] * len(data)
    amounts = [''] * len(data)
    tax_rate = [''] * len(data)
    legacy_debts = [''] * len(data)
    pbis = [''] * len(data)
    text = [''] * len(data)

    for (i, row) in zip(range(0, len(data)), data):

        groups[i] = row['Group']
        companies[i] = row['Company']
        interest_types[i] = row['Interest Type']
        amounts[i] = row['Amount (€)']
        tax_rate[i] = row['Tax Rate (%)']
        legacy_debts[i] = row['Legacy Debt']
        pbis[i] = row['PBI Amount (€)']
        text[i] = row['Text Description']

    store_data = {'Group': groups, 'Company': companies, 'Interest Type': interest_types,
                  'Amount (€)': amounts, 'Tax Rate (%)': tax_rate, 'Legacy Debt': legacy_debts,
                  'PBI Amount (€)': pbis, 'Text Description': text}
    data_list = [{'ebc_table_data': store_data}]
    return data_list


##----------CLEARING FIELDS CALLBACK---------

# clearing data for additional companies
@dash_app.callback(
    Output('ebc_group_dd', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebc_company_dd', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebc_interest_dd', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebc_amount_input', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebc_tax_dd', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebc_legacy_toggle_switch', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False

@dash_app.callback(
    Output('ebc_pbi_input', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebc_text_description', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebc_pbi_toggle_switch', 'value'),
    Input('save_ebc', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


##----------CURRENCY DESCRIPTION CALLBACK-------
@dash_app.callback(
    Output('amount_description', 'children'),
    Input('spot_rate_store', 'data')
    # Input('currency_dd', 'value')
)
def change_text(spot_rate_store):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'Euro (€)':
            return html.H6("Amount (€)")
        else:
            if currency == 'GBP (£)':
                return html.H6("Amount (£)")
            elif currency == 'USD ($)':
                return html.H6("Amount ($)")
            else:
                return html.H6("Amount")
    else:
        return html.H6("Amount (€)")


# "Public Benefit Infrastructure (€)"
@dash_app.callback(
    Output('pbi_description_currency', 'children'),
    Input('spot_rate_store', 'data')
    # Input('currency_dd', 'value')
)
def change_text(spot_rate_store):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'Euro (€)':
            return html.H6("Public Benefit Infrastructure (€)")
        else:
            if currency == 'USD ($)':
                return html.H6("Public Benefit Infrastructure ($)")
            elif currency == 'GBP (£)':
                return html.H6("Public Benefit Infrastructure (£)")
            else:
                return html.H6("Public Benefit Infrastructure")
    else:
        return html.H6("Public Benefit Infrastructure (€)")


##-------converting & displaying amount in euro callback ------------

@dash_app.callback(
    Output('ebc_amount_in_euro_text', 'style'),
    Input('spot_rate_store', 'data'),
    # Input('currency_dd', 'value'),
    Input('ebc_amount_input', 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'USD ($)' and amount is not None:
            return {'display': 'block'}
        if currency == 'GBP (£)' and amount is not None:
            return {'display': 'block'}
        if currency == 'Other' and amount is not None:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebc_amount_in_euro_text', 'children'),
    Input('spot_rate_store', 'data'),
    #   Input('currency_dd', 'value'),
    Input('ebc_amount_input', 'value'),
    #   Input('spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            if spot_rate != "No Spot Rate Entered":
                return "Amount in €: "
            else:
                return "Please enter spot rate"


@dash_app.callback(
    Output('ebc_amount_in_euro_value', 'style'),
    Input('spot_rate_store', 'data'),
    Input('ebc_amount_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency != 'Euro (€)' and amount != None and amount != '':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebc_amount_in_euro_value', 'children'),
    Input('spot_rate_store', 'data'),
    Input('ebc_amount_input', 'value'),
    #   Input('spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            try:
                float(spot_rate)
                value = float(float(amount) / float(spot_rate))
                return '{:,.2f}'.format(value)
                #return round(float(float(amount) / float(spot_rate)), 2)
            except ValueError:
                return ""


##-------converting & displaying PBI amount in euro callback ------------

@dash_app.callback(
    Output('ebc_pbi_amount_in_euro_text', 'style'),
    Input('spot_rate_store', 'data'),
    # Input('currency_dd', 'value'),
    Input('ebc_pbi_input', 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'USD ($)' and amount != None:
            return {'display': 'block'}
        if currency == 'GBP (£)' and amount != None:
            return {'display': 'block'}
        if currency == 'Other' and amount != None:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebc_pbi_amount_in_euro_text', 'children'),
    Input('spot_rate_store', 'data'),
    #   Input('currency_dd', 'value'),
    Input('ebc_pbi_input', 'value'),
    #   Input('spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            if spot_rate != "No Spot Rate Entered":
                return "Amount in €: "
            else:
                return "Please enter spot rate"


@dash_app.callback(
    Output('ebc_pbi_amount_in_euro_value', 'style'),
    Input('spot_rate_store', 'data'),
    Input('ebc_pbi_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency != 'Euro (€)' and amount != None and amount != '':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebc_pbi_amount_in_euro_value', 'children'),
    Input('spot_rate_store', 'data'),
    Input('ebc_pbi_input', 'value'),
    #   Input('spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            try:
                float(spot_rate)
                value = float(float(amount) / float(spot_rate))
                return '{:,.2f}'.format(value)
                #return round(float(float(amount) / float(spot_rate)), 2)
            except ValueError:
                return ""


##-----------EBC CALCULATION CALLBACK----------

@dash_app.callback(Output('ebc-output', 'children'),
                   # Input('ebc-calculate', 'n_clicks'),
                   Input('ebc_table', 'data')
                   )
def ebc_calc(data):
    num_rows = len(data)
    if num_rows == 0:
        return "Not yet calculated"
    else:
        sum1 = sum2 = sum3 = 0
        for row in data:
            if row['Interest Type'] == "Interest Expense":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum1 = float(float(row['Amount (€)']) - pbi_val) * float(row['Tax Rate (%)']) / corporate_tax
                    sum1 = sum1 + row_sum1
                except ValueError:
                    row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    sum1 = sum1 + row_sum1

                if row['Legacy Debt'] == 'Y':
                    row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                else:
                    row_sum2 = 0
                sum2 = sum2 + row_sum2

            if row['Interest Type'] == "Interest Income":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum3 = float(float(row['Amount (€)']) - pbi_val) * float(row['Tax Rate (%)']) / corporate_tax
                    sum3 = sum3 + row_sum3
                except ValueError:
                    row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    sum3 = sum3 + row_sum3

        tot_sum = sum1 - sum2 - sum3
        formatted_tot_sum = '€{:,.2f}'.format(tot_sum)
        # n_clicks=0
        return formatted_tot_sum  # , n_clicks


##-----------EBC WORKINGS CALLBACK------------

@dash_app.callback(
    Output('ebc_company_workings_dd', 'options'),
    Output('ebc_company_workings_dd', 'value'),
    Input('ebc_table', 'data')
)
def company_dropdown(data):
    num_rows = len(data)
    if num_rows == 0:
        companies = ['No Companies Entered']
        options = [{'label': cmpy, 'value': cmpy} for cmpy in companies]
        value = companies[0]
        return options, value
    else:
        companies_init = ['All']
        companies1 = [None] * num_rows
        for (i, row) in zip(range(0, num_rows), data):
            companies1[i] = row['Company']
        companies2 = sorted(list(set(companies1)))
        companies = companies_init + companies2
        options = [{'label': cmpy, 'value': cmpy} for cmpy in companies]
        value = companies[0]
        return options, value


@dash_app.callback(Output('ebc-workings-output', 'children'),
                   # Input('ebc-workings', 'n_clicks'),
                   Input('ebc_table', 'data'),
                   Input('ebc_company_workings_dd', 'value')
                   )
def ebc_calc(data, company_selected):
    num_rows = len(data)
    if num_rows > 0:
        sum1 = sum2 = sum3 = 0
        taxsum1 = taxsum2 = taxsum3 = 0
        legacyDebtSum12 = 0
        legacyDebtSum25 = 0
        legacyDebtSum33 = 0
        int_income12 = 0
        int_income25 = 0
        int_income33 = 0

        if company_selected == 'All' or company_selected == '' or company_selected is None:
            # pbi_expense_sum = 0
            for row in data:
                if row['Interest Type'] == "Interest Expense":
                    try:
                        pbi_val = float(row['PBI Amount (€)'])
                        row_sum1 = float(float(row['Amount (€)']) - pbi_val) * float(
                            row['Tax Rate (%)']) / corporate_tax
                        sum1 = sum1 + row_sum1
                    except ValueError:
                        row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                        sum1 = sum1 + row_sum1

                    if row['Legacy Debt'] == 'Y':
                        row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                    else:
                        row_sum2 = 0
                    sum2 = sum2 + row_sum2

                    if float(row['Tax Rate (%)']) == 12.5:
                        try:
                            float(row['PBI Amount (€)'])
                            taxsum1 = taxsum1 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                        except ValueError:
                            taxsum1 = taxsum1 + float(row['Amount (€)'])
                        if row['Legacy Debt'] == 'Y':
                            legacyDebtSum12 = legacyDebtSum12 + float(row['Amount (€)'])
                    elif float(row['Tax Rate (%)']) == 25:
                        try:
                            float(row['PBI Amount (€)'])
                            taxsum2 = taxsum2 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                        except ValueError:
                            taxsum2 = taxsum2 + float(row['Amount (€)'])
                        if row['Legacy Debt'] == 'Y':
                            legacyDebtSum25 = legacyDebtSum25 + float(row['Amount (€)'])
                        # taxsum2 = taxsum2 + float(row['Amount (€)'])
                    elif float(row['Tax Rate (%)']) == 33:
                        try:
                            float(row['PBI Amount (€)'])
                            taxsum3 = taxsum3 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                        except ValueError:
                            taxsum3 = taxsum3 + float(row['Amount (€)'])
                        if row['Legacy Debt'] == 'Y':
                            legacyDebtSum33 = legacyDebtSum33 + float(row['Amount (€)'])

                if row['Interest Type'] == "Interest Income":
                    try:
                        pbi_val = float(row['PBI Amount (€)'])
                        row_sum3 = float(float(row['Amount (€)']) - pbi_val) * float(
                            row['Tax Rate (%)']) / corporate_tax
                        sum3 = sum3 + row_sum3
                    except ValueError:
                        row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                        sum3 = sum3 + row_sum3

                    if float(row['Tax Rate (%)']) == 12.5:
                        try:
                            float(row['PBI Amount (€)'])
                            int_income12 = int_income12 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                        except ValueError:
                            int_income12 = int_income12 + float(row['Amount (€)'])
                    elif float(row['Tax Rate (%)']) == 25:
                        try:
                            float(row['PBI Amount (€)'])
                            int_income25 = int_income25 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                        except ValueError:
                            int_income12 = int_income12 + float(row['Amount (€)'])
                        # taxsum2 = taxsum2 + float(row['Amount (€)'])
                    elif float(row['Tax Rate (%)']) == 33:
                        try:
                            float(row['PBI Amount (€)'])
                            int_income33 = int_income33 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                        except ValueError:
                            int_income33 = int_income33 + float(row['Amount (€)'])
        else:
            for row in data:
                if row['Company'] == company_selected:
                    if row['Interest Type'] == "Interest Expense":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum1 = float(float(row['Amount (€)']) - pbi_val) * float(
                                row['Tax Rate (%)']) / corporate_tax
                            sum1 = sum1 + row_sum1
                        except ValueError:
                            row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                            sum1 = sum1 + row_sum1

                        if row['Legacy Debt'] == 'Y':
                            row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                        else:
                            row_sum2 = 0
                        sum2 = sum2 + row_sum2

                        if float(row['Tax Rate (%)']) == 12.5:
                            try:
                                float(row['PBI Amount (€)'])
                                taxsum1 = taxsum1 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                            except ValueError:
                                taxsum1 = taxsum1 + float(row['Amount (€)'])
                            if row['Legacy Debt'] == 'Y':
                                legacyDebtSum12 = legacyDebtSum12 + float(row['Amount (€)'])
                        elif float(row['Tax Rate (%)']) == 25:
                            try:
                                float(row['PBI Amount (€)'])
                                taxsum2 = taxsum2 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                            except ValueError:
                                taxsum2 = taxsum2 + float(row['Amount (€)'])
                            if row['Legacy Debt'] == 'Y':
                                legacyDebtSum25 = legacyDebtSum25 + float(row['Amount (€)'])
                            # taxsum2 = taxsum2 + float(row['Amount (€)'])
                        elif float(row['Tax Rate (%)']) == 33:
                            try:
                                float(row['PBI Amount (€)'])
                                taxsum3 = taxsum3 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                            except ValueError:
                                taxsum3 = taxsum3 + float(row['Amount (€)'])
                            if row['Legacy Debt'] == 'Y':
                                legacyDebtSum33 = legacyDebtSum33 + float(row['Amount (€)'])

                    if row['Interest Type'] == "Interest Income":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum3 = float(float(row['Amount (€)']) - pbi_val) * float(
                                row['Tax Rate (%)']) / corporate_tax
                            sum3 = sum3 + row_sum3
                        except ValueError:
                            row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                            sum3 = sum3 + row_sum3

                        if float(row['Tax Rate (%)']) == 12.5:
                            try:
                                float(row['PBI Amount (€)'])
                                int_income12 = int_income12 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                            except ValueError:
                                int_income12 = int_income12 + float(row['Amount (€)'])
                        elif float(row['Tax Rate (%)']) == 25:
                            try:
                                float(row['PBI Amount (€)'])
                                int_income25 = int_income25 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                            except ValueError:
                                int_income12 = int_income12 + float(row['Amount (€)'])
                            # taxsum2 = taxsum2 + float(row['Amount (€)'])
                        elif float(row['Tax Rate (%)']) == 33:
                            try:
                                float(row['PBI Amount (€)'])
                                int_income33 = int_income33 + float(float(row['Amount (€)']) - float(row['PBI Amount (€)']))
                            except ValueError:
                                int_income33 = int_income33 + float(row['Amount (€)'])

        taxsum22 = taxsum2 * 0.25
        taxsum33 = taxsum3 * 0.33
        taxsum222 = taxsum22 / 0.125
        taxsum333 = taxsum33 / 0.125
        tot_int_exp1 = taxsum1 + taxsum222 + taxsum333

        legacyDebtSum25_tax = legacyDebtSum25 * 0.25
        legacyDebtSum33_tax = legacyDebtSum33 * 0.33
        legacyDebtSum25_taxx = legacyDebtSum25_tax / 0.125
        legacyDebtSum33_taxx = legacyDebtSum33_tax / 0.125
        tot_leg_debt = legacyDebtSum12 + legacyDebtSum25_taxx + legacyDebtSum33_taxx

        int_income_25_tax = int_income25 * 0.25
        int_income_33_tax = int_income33 * 0.33
        int_income_25_taxx = int_income_25_tax / 0.125
        int_income_33_taxx = int_income_33_tax / 0.125
        tot_int_income = int_income12 + int_income_25_taxx + int_income_33_taxx
        tot_int_income1 = tot_int_income

        tot_sum = sum1 - sum2 - sum3
        formatted_tot_sum = '€{:,.2f}'.format(tot_sum)
        workings = html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div('Interest Expense (ignore PBI): ', style={'font-size': '80%'}),
                    html.Div('LESS Legacy Debt: ', style={'font-size': '80%'}),
                    html.Div('LESS Interest Income (ignore PBI): ', style={'font-size': '80%'}),
                    html.Div('=', style={'font-size': '80%'})
                ],
                    width=6),

                dbc.Col([
                    html.Div('€{:,.2f}'.format(tot_int_exp1), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(tot_leg_debt), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(tot_int_income1)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.B('{}'.format(formatted_tot_sum)), style={'text-align': 'right', 'font-size': '80%'})

                ], width=3)
            ]),

            html.Br(),

            html.Div(html.U(html.B('Interest Expense (Ignore PBI)')), style={'font-size': '80%'}),
            dbc.Row([
                dbc.Col([
                    html.Div('Interest Expense (ignore PBI) @ 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Interest Expense (ignore PBI) @ 25%: ', style={'font-size': '80%'}),
                    html.Div('= ', style={'font-size': '80%'}),
                    html.Div('DIVIDED BY 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Interest Expense (ignore PBI) @ 33%: ', style={'font-size': '80%'}),
                    html.Div('= ', style={'font-size': '80%'}),
                    html.Div('DIVIDED BY 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Total Interest Expense (ignore PBI): ', style={'font-size': '80%'}),
                ],
                    width=6
                ),

                dbc.Col([
                    html.Div('€{:,.2f}'.format(taxsum1), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div('€{:,.2f}'.format(taxsum2), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(taxsum22)), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(taxsum222), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div('€{:,.2f}'.format(taxsum3), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(taxsum33)), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(taxsum333), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div(html.B('€{:,.2f}'.format(tot_int_exp1)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                ],
                    width=3
                )
            ]),

            html.Br(),
            html.Br(),
            html.Div(html.U(html.B('Legacy Debt')), style={'font-size': '80%'}),
            dbc.Row([
                dbc.Col([
                    html.Div('Legacy Debt @ 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Legacy Debt @ 25%: ', style={'font-size': '80%'}),
                    html.Div('= ', style={'font-size': '80%'}),
                    html.Div('DIVIDED BY 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Legacy Debt @ 33%: ', style={'font-size': '80%'}),
                    html.Div('= ', style={'font-size': '80%'}),
                    html.Div('DIVIDED BY 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Total Legacy Debt: ', style={'font-size': '80%'}),
                ],
                    width=6
                ),

                dbc.Col([
                    html.Div('€{:,.2f}'.format(legacyDebtSum12), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div('€{:,.2f}'.format(legacyDebtSum25), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(legacyDebtSum25_tax)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(legacyDebtSum25_taxx),
                             style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div('€{:,.2f}'.format(legacyDebtSum33), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(legacyDebtSum33_tax)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(legacyDebtSum33_taxx),
                             style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div(html.B('€{:,.2f}'.format(tot_leg_debt)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                ],
                    width=3
                )
            ]),

            html.Br(),
            html.Br(),
            html.Div(html.U(html.B('Interest Income (Ignore PBI)')), style={'font-size': '80%'}),
            dbc.Row([
                dbc.Col([
                    # html.Div(html.U('Interest Expense (Ignore PBI)'), style={'font-size': '80%'}),
                    html.Div('Interest Income @ 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Interest Income @ 25%: ', style={'font-size': '80%'}),
                    html.Div('= ', style={'font-size': '80%'}),
                    html.Div('DIVIDED BY 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Interest Income @ 33%: ', style={'font-size': '80%'}),
                    html.Div('= ', style={'font-size': '80%'}),
                    html.Div('DIVIDED BY 12.5%: ', style={'font-size': '80%'}),
                    html.Br(),
                    html.Div('Total Interest Income: ', style={'font-size': '80%'}),
                ],
                    width=6
                ),

                dbc.Col([
                    html.Div('€{:,.2f}'.format(int_income12), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div('€{:,.2f}'.format(int_income25), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(int_income_25_tax)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(int_income_25_taxx), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div('€{:,.2f}'.format(int_income33), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(int_income_33_tax)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(int_income_33_taxx), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Br(),
                    html.Div(html.B('€{:,.2f}'.format(tot_int_income1)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                ],
                    width=3
                )
            ]),
        ])
        # n_clicks=0
        return workings


##-----------EBC DM WORKINGS CALLBACK------------------
@dash_app.callback(Output('ebc-dm-workings-output', 'children'),
                   # Input('ebc-dm-workings', 'n_clicks'),
                   Input('ebc_table', 'data'),
                   Input('ebc_company_workings_dd', 'value')
                   )
def ebc_calc(data, company_selected):
    num_rows = len(data)
    if num_rows > 0:
        sum4 = sum5 = sum6 = 0
        if company_selected == 'All' or company_selected == '' or company_selected is None:
            for row in data:
                if row['Interest Type'] == "Interest Expense":
                    try:
                        pbi_val = float(row['PBI Amount (€)'])
                        row_sum4 = float(float(row['Amount (€)']) - pbi_val)
                        sum4 = sum4 + row_sum4
                    except ValueError:
                        row_sum4 = float(float(row['Amount (€)']))
                        sum4 = sum4 + row_sum4

                    if row['Legacy Debt'] == 'Y':
                        row_sum5 = float(row['Amount (€)'])
                    else:
                        row_sum5 = 0
                    sum5 = sum5 + row_sum5
                if row['Interest Type'] == "Interest Income":
                    try:
                        pbi_val = float(row['PBI Amount (€)'])
                        row_sum6 = float(float(row['Amount (€)']) - pbi_val)
                        sum6 = sum6 + row_sum6
                    except ValueError:
                        row_sum6 = float(float(row['Amount (€)']))
                        sum6 = sum6 + row_sum6
        else:
            for row in data:
                if row['Company'] == company_selected:
                    if row['Interest Type'] == "Interest Expense":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum4 = float(float(row['Amount (€)']) - pbi_val)
                            sum4 = sum4 + row_sum4
                        except ValueError:
                            row_sum4 = float(float(row['Amount (€)']))
                            sum4 = sum4 + row_sum4
                        if row['Legacy Debt'] == 'Y':
                            row_sum5 = float(row['Amount (€)'])
                        else:
                            row_sum5 = 0
                        sum5 = sum5 + row_sum5
                    if row['Interest Type'] == "Interest Income":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum6 = float(float(row['Amount (€)']) - pbi_val)
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
                ], width=6),
                dbc.Col([
                    html.Div('€{:,.2f}'.format(sum4), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div('€{:,.2f}'.format(sum5), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('€{:,.2f}'.format(sum6)), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.B('{}'.format(formatted_tot_sum2)), style={'text-align': 'right', 'font-size': '80%'})
                ], width=3)
            ])

        ])
        return workings


###-----------------EBC STORE CALLBACK--------------

@dash_app.callback(
    Output('ebc_store', 'data'),
    Output('ebc_store_dm', 'data'),
    Output('ebc_store_intcalc', 'data'),
    Input('ebc_table', 'data')
)
def return_ebc(inputted_data):
    num_rows = len(inputted_data)
    if num_rows == 0:
        datalist = [{'Company': 'All', 'Group': 'All', 'ebc': 'No Details Entered'}]
        datalist_dm = [{'Company': 'All', 'Group': 'All', 'ebc_dm': 'No Details Entered'}]
        datalist_intcalc = [{'Company': 'All', 'Group': 'All', 'intcalc': 0}]

    if num_rows > 0:
        datalist = []
        datalist_dm = []
        datalist_intcalc = []

        # group entry
        groupsum1 = groupsum2 = groupsum3 = 0
        groupsum4 = groupsum5 = groupsum6 = 0
        for row in inputted_data:
            if row['Interest Type'] == "Interest Expense":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum1 = float(float(row['Amount (€)']) - pbi_val) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum1 = groupsum1 + row_sum1
                    row_sum4 = float(float(row['Amount (€)']) - pbi_val)
                    groupsum4 = groupsum4 + row_sum4
                except ValueError:
                    row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum1 = groupsum1 + row_sum1
                    row_sum4 = float(float(row['Amount (€)']))
                    groupsum4 = groupsum4 + row_sum4

                if row['Legacy Debt'] == 'Y':
                    row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                    row_sum5 = float(row['Amount (€)'])
                else:
                    row_sum2 = 0
                    row_sum5 = 0
                groupsum2 = groupsum2 + row_sum2
                groupsum5 = groupsum5 + row_sum5

            if row['Interest Type'] == "Interest Income":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum3 = float(float(row['Amount (€)']) - pbi_val) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum3 = groupsum3 + row_sum3
                    row_sum6 = float(float(row['Amount (€)']) - pbi_val)
                    groupsum6 = groupsum6 + row_sum6
                except ValueError:
                    row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum3 = groupsum3 + row_sum3
                    row_sum6 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum6 = groupsum6 + row_sum6
        group_tot_sum = groupsum1 - groupsum2 - groupsum3
        group_tot_sum_dm = groupsum4 - groupsum5 - groupsum6
        datalist = datalist + [{'Company': 'All', 'Group': 'All', 'ebc': '€{:,.2f}'.format(group_tot_sum)}]
        datalist_dm = datalist_dm + [{'Company': 'All', 'Group': 'All', 'ebc_dm': '€{:,.2f}'.format(group_tot_sum_dm)}]
        datalist_intcalc = datalist_intcalc + [{'Company': 'All', 'Group': 'All', 'intcalc': groupsum2}]

        # get list of companies

        company_list1 = [None] * num_rows
        for (i, row) in zip(range(0, num_rows), inputted_data):
            company_list1[i] = row['Company']
        company_list = sorted(list(set(company_list1)))

        for company in company_list:
            sum1 = sum2 = sum3 = 0
            sum4 = sum5 = sum6 = 0
            for row in inputted_data:
                if row['Company'] == company:
                    group = row['Group']
                    if row['Interest Type'] == "Interest Expense":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum1 = float(float(row['Amount (€)']) - pbi_val) * float(
                                row['Tax Rate (%)']) / corporate_tax
                            sum1 = sum1 + row_sum1
                            row_sum4 = float(float(row['Amount (€)']) - pbi_val)
                            sum4 = sum4 + row_sum4
                        except ValueError:
                            row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                            sum1 = sum1 + row_sum1
                            row_sum4 = float(float(row['Amount (€)']))
                            sum4 = sum4 + row_sum4

                    if row['Legacy Debt'] == 'Y':
                        row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                        row_sum5 = float(row['Amount (€)'])
                    else:
                        row_sum2 = 0
                        row_sum5 = 0
                    sum2 = sum2 + row_sum2
                    sum5 = sum5 + row_sum5

                    if row['Interest Type'] == "Interest Income":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum3 = float(float(row['Amount (€)']) - pbi_val) * float(
                                row['Tax Rate (%)']) / corporate_tax
                            sum3 = sum3 + row_sum3
                            row_sum6 = float(float(row['Amount (€)']) - pbi_val)
                            sum6 = sum6 + row_sum6
                        except ValueError:
                            row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                            sum3 = sum3 + row_sum3
                            row_sum6 = float(float(row['Amount (€)']))
                            sum6 = sum6 + row_sum6
            tot_sum = sum1 - sum2 - sum3
            tot_sum_dm = sum4 - sum5 - sum6
            datalist = datalist + [{'Company': company, 'Group': group, 'ebc': '€{:,.2f}'.format(tot_sum)}]
            datalist_dm = datalist_dm + [{'Company': company, 'Group': group, 'ebc_dm': '€{:,.2f}'.format(tot_sum_dm)}]
            datalist_intcalc = datalist_intcalc + [{'Company': company, 'Group': group, 'intcalc': sum2}]
            #print(datalist)
    return datalist, datalist_dm, datalist_intcalc


###---INTEREST SPARE CAPACITY STORE---------------
@dash_app.callback(
    Output('ebc_store_spareCap', 'data'),
    Input('ebc_table', 'data'),
)
def return_ebc(data):
    num_rows = len(data)
    if num_rows == 0:
        spare_cap = 0
        datalist = [{'Company': 'All', 'Group': 'All', 'spare_capacity': spare_cap}]
    else:
        # get list of companies
        company_list1 = [None] * num_rows
        for (i, row) in zip(range(0, num_rows), data):
            company_list1[i] = row['Company']
        company_list = sorted(list(set(company_list1)))

        datalist = []
        group_spare_cap = 0
        for row in data:
            if row['Interest Type'] == "Interest Spare Capacity":
                group_spare_cap = group_spare_cap + float(row['Amount (€)'])
        datalist = datalist + [{'Company': 'All', 'Group': 'All', 'spare_capacity': group_spare_cap}]

        for company in company_list:
            spare_cap = 0
            for row in data:
                group = row['Group']
                if row['Company'] == company:
                    if row['Interest Type'] == "Interest Spare Capacity":
                        spare_cap = spare_cap + float(row['Amount (€)'])
            datalist = datalist + [{'Company': company, 'Group': group, 'spare_capacity': spare_cap}]
    return datalist


##-------GET GROUP DROPDOWN DATA FROM HOME CALLBACK-------

@dash_app.callback(
    Output("ebc_group_dd", "options"),
    Input("home_store", "data"),
)
def update_group_dropdown(data):
    if data != [{}]:
        group_data = data[0]
        if group_data['group'] != []:
            return [{"label": i, "value": i} for i in group_data['group']]
        else:
            return [{"label": "No Groups", "value": "No Groups"}]
    else:
        return [{'label': grp, "value": grp} for grp in group_dummy]


##-------GET COMPANY DROPDOWN DATA FROM HOME CALLBACK-------

@dash_app.callback(
    Output("ebc_company_dd", "options"),
    Input("home_store", "data"),
)
def update_company_dropdown(data):
    if data != [{}]:
        company_data = data[1]
        if company_data['company'] != []:
            return [{"label": i, "value": i} for i in company_data['company']]
        else:
            return [{"label": "No Company", "value": "No Company"}]
    else:
        return [{'label': cmp, "value": cmp} for cmp in company_dummy]


###---EBC TOGGLE COLOUR CALLBACK---
@dash_app.callback(
    Output('ebc_legacy_no', 'children'),
    Input('ebc_legacy_toggle_switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('ebc_legacy_yes', 'children'),
    Input('ebc_legacy_toggle_switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


@dash_app.callback(
    Output('ebc_pbi_no', 'children'),
    Input('ebc_pbi_toggle_switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('ebc_pbi_yes', 'children'),
    Input('ebc_pbi_toggle_switch', 'value')
)
def bold(switch):
    if switch == True:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


##---------------results table calback----------
@dash_app.callback(Output('ebc_results_table', 'data'),
                   Input('ebc_table', 'data'),
                   State('ebc_results_table', 'columns')
                   )
def ebc_calc(inputted_data, results_columns):
    num_rows = len(inputted_data)
    # if num_rows == 0:
    #     return []
    if num_rows > 0:
        results_data = []

        # get list of companies
        company_list1 = [None] * num_rows
        for (i, row) in zip(range(0, num_rows), inputted_data):
            company_list1[i] = row['Company']
        company_list = sorted(list(set(company_list1)))

        for company in company_list:
            sum1 = 0
            sum2 = 0
            sum3 = 0
            sum4 = sum5 = sum6 = 0
            for row in inputted_data:
                if row['Company'] == company:
                    group = row['Group']
                    if row['Interest Type'] == "Interest Expense":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum1 = float(float(row['Amount (€)']) - pbi_val) * float(
                                row['Tax Rate (%)']) / corporate_tax
                            sum1 = sum1 + row_sum1
                            row_sum4 = float(float(row['Amount (€)']) - pbi_val)
                            sum4 = sum4 + row_sum4
                        except ValueError:
                            row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                            sum1 = sum1 + row_sum1
                            row_sum4 = float(float(row['Amount (€)']))
                            sum4 = sum4 + row_sum4

                    if row['Legacy Debt'] == 'Y':
                        row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                        row_sum5 = float(row['Amount (€)'])
                    else:
                        row_sum2 = 0
                        row_sum5 = 0
                    sum2 = sum2 + row_sum2
                    sum5 = sum5 + row_sum5

                    if row['Interest Type'] == "Interest Income":
                        try:
                            pbi_val = float(row['PBI Amount (€)'])
                            row_sum3 = float(float(row['Amount (€)']) - pbi_val) * float(
                                row['Tax Rate (%)']) / corporate_tax
                            sum3 = sum3 + row_sum3
                            row_sum6 = float(float(row['Amount (€)']) - pbi_val)
                            sum6 = sum6 + row_sum6
                        except ValueError:
                            row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                            sum3 = sum3 + row_sum3
                            row_sum6 = float(float(row['Amount (€)']))
                            sum6 = sum6 + row_sum6
            tot_sum = sum1 - sum2 - sum3
            tot_sum_dm = sum4 - sum5 - sum6
            company_result = [group, company, '{:,.2f}'.format(tot_sum), '{:,.2f}'.format(tot_sum_dm)]
            results_data.append({
                results_columns[j]['id']: company_result[j] for j in range(0, 4)
            })

        groupsum1 = groupsum2 = groupsum3 = 0
        groupsum4 = groupsum5 = groupsum6 = 0
        for row in inputted_data:
            group = row['Group']
            #            if row['Group'] == group:
            if row['Interest Type'] == "Interest Expense":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum1 = float(float(row['Amount (€)']) - pbi_val) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum1 = groupsum1 + row_sum1
                    row_sum4 = float(float(row['Amount (€)']) - pbi_val)
                    groupsum4 = groupsum4 + row_sum4
                except ValueError:
                    row_sum1 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum1 = groupsum1 + row_sum1
                    row_sum4 = float(float(row['Amount (€)']))
                    groupsum4 = groupsum4 + row_sum4

                if row['Legacy Debt'] == 'Y':
                    row_sum2 = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                    row_sum5 = float(row['Amount (€)'])
                else:
                    row_sum2 = 0
                    row_sum5 = 0
                groupsum2 = groupsum2 + row_sum2
                groupsum5 = groupsum5 + row_sum5

            if row['Interest Type'] == "Interest Income":
                try:
                    pbi_val = float(row['PBI Amount (€)'])
                    row_sum3 = float(float(row['Amount (€)']) - pbi_val) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum3 = groupsum3 + row_sum3
                    row_sum6 = float(float(row['Amount (€)']) - pbi_val)
                    groupsum6 = groupsum6 + row_sum6
                except ValueError:
                    row_sum3 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum3 = groupsum3 + row_sum3
                    row_sum6 = float(float(row['Amount (€)'])) * float(row['Tax Rate (%)']) / corporate_tax
                    groupsum6 = groupsum6 + row_sum6
        group_tot_sum = groupsum1 - groupsum2 - groupsum3
        group_tot_sum_dm = groupsum4 - groupsum5 - groupsum6
        group_result = [group, 'Group Total', '{:,.2f}'.format(group_tot_sum), '{:,.2f}'.format(group_tot_sum_dm)]
        results_data.append({
            results_columns[j]['id']: group_result[j] for j in range(0, len(group_result))
        })
        return results_data


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------TAX EBITDA PAGE-------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
                        
                        html.Div(html.H2("Tax EBITDA", className="card-title", style={'color': kpmgBlue_hash}), style={'display': 'inline-block'}),
                        
                        html.Div(html.I(id="popover-target3", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left':'10px', 'display': 'inline-block'})
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

ebitda_layout = html.Div([
    card_tax_ebitda,
    html.P(""),
    ebitda_table_section,
    html.P(""),
    ebitda_results_table_section,
    html.P(""),
    ebitda_results_card
])


##-------------------------------TAX EBITDA CALLBACKS--------------------------

# Hide PBI until user clicks "Yes"
@dash_app.callback(
    Output(component_id="input_loss_ebitda", component_property='style'),
    [Input(component_id='ebitda_loss_toggle_switch', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state == True:
        return {'display': 'block', 'width': '80%'}
    if visibility_state == False:
        return {'display': 'none'}


@dash_app.callback(
    Output(component_id="input_pbipp_ebitda", component_property='style'),
    [Input(component_id='ebitda_pbi_toggle_switch', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state == True:
        return {'display': 'block', 'width': '80%'}
    if visibility_state == False:
        return {'display': 'none'}


@dash_app.callback(
    Output(component_id="input_deduct_ebitda", component_property='style'),
    [Input(component_id='ebitda_pbi_ded_toggle_switch', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state == True:
        return {'display': 'block', 'width': '80%'}
    if visibility_state == False:
        return {'display': 'none'}


##-------------SHOW DATATABLE CALLBACK----------

# Hide data table until user clicks "See Data"
@dash_app.callback(
    Output(component_id='ebitda_table_details', component_property='style'),
    [Input(component_id='save_tax_ebitda', component_property='n_clicks')])
def show_hide_element_ebitda(n_clicks):
    if n_clicks > 0:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


##------------UPDATE DATATABLE CALLBACK---------


@dash_app.callback(
    Output('ebitda_table', 'data'),
    Input('save_tax_ebitda', 'n_clicks'),
    State('ebitda_table', 'data'),
    State('ebitda_table', 'columns'),
    State('group_name_ebitda', 'value'),
    State('company_name_ebitda', 'value'),
    State('interest_group_ebitda', 'value'),
    State('amount_input_ebitda', 'value'),
    State('tax_rate_ebitda', 'value'),
    State('input_pbipp_ebitda', 'value'),
    State('input_deduct_ebitda', 'value'),
    State('ebitda_table_store', 'data'),
    State('spot_rate_store', 'data'),
    State('ebitda_pbi_interest_amount_in_euro_value', 'children'),
    State('ebitda_pbi_amount_in_euro_value', 'children'),
    State('ebitda_amount_in_euro_value', 'children'),
    State('ebitda_loss_toggle_switch', 'value')
)
def produce_home_datatable_ebitda(n_clicks, rows1, columns, group_name_ebitda, company_name_ebitda,
                                  interest_group_ebitda, amount_input_ebitda, tax_rate_ebitda,
                                  input_pbipp_ebitda, input_deduct_ebitda, store, spot_rate_store, interest_euro,
                                  pbi_euro, amount_euro, toggle):
    if n_clicks == 0:
        if store == [{}] or store == None:
            return []
        elif store != [{}]:
            ebitda_table = store[0]
            ebitda_table_data = ebitda_table['ebitda_table_data']
            ebitda_table_df = pd.DataFrame(ebitda_table_data)

            data = ebitda_table_df.to_dict('records')
            return data

    if n_clicks > 0:
        if group_name_ebitda is None or company_name_ebitda is None or interest_group_ebitda is None or amount_input_ebitda is None or tax_rate_ebitda is None:
            raise PreventUpdate
        else:
            details = spot_rate_store[0]
            currency = details['currency']
            if currency == 'Euro (€)':
                if toggle:
                    amount_inputted = 0
                    loss_inputted = amount_input_ebitda
                else:
                    amount_inputted = amount_input_ebitda
                    loss_inputted = 0

                # pbi not inputted
                if input_pbipp_ebitda is None or input_pbipp_ebitda == '':
                    results_ebitda = [group_name_ebitda, company_name_ebitda, interest_group_ebitda, amount_inputted,
                                      tax_rate_ebitda, loss_inputted, 0, 0, 12.5]
                    rows1.append({
                        columns[i]['id']: results_ebitda[i] for i in range(0, len(ebitda_df.columns))
                    })

                # pbi inputted
                else:

                    if input_deduct_ebitda is None or input_deduct_ebitda == '':
                        results_ebitda = [group_name_ebitda, company_name_ebitda, interest_group_ebitda,
                                          amount_inputted,
                                          tax_rate_ebitda, loss_inputted, input_pbipp_ebitda, 0]
                    else:
                        results_ebitda = [group_name_ebitda, company_name_ebitda, interest_group_ebitda,
                                          amount_inputted,
                                          tax_rate_ebitda, loss_inputted, input_pbipp_ebitda, input_deduct_ebitda]

                    rows1.append({
                        columns[i]['id']: results_ebitda[i] for i in range(0, len(ebitda_df.columns))
                    })
            else:
                if group_name_ebitda is None or company_name_ebitda is None or interest_group_ebitda is None or \
                        amount_euro is None or tax_rate_ebitda is None:
                    raise PreventUpdate

                else:
                    if toggle == True:
                        amount_inputted = 0
                        loss_inputted = float(amount_euro)
                    else:
                        amount_inputted = float(amount_euro)
                        loss_inputted = 0

                    if pbi_euro is None or pbi_euro == '':
                        results_ebitda = [group_name_ebitda, company_name_ebitda, interest_group_ebitda,
                                          '{:,.2f}'.format(amount_inputted),
                                          tax_rate_ebitda, '{:,.2f}'.format(loss_inputted), 0, 0, 12.5]
                        rows1.append({
                            columns[i]['id']: results_ebitda[i] for i in range(0, len(ebitda_df.columns))
                        })
                    else:
                        results_ebitda = [group_name_ebitda, company_name_ebitda, interest_group_ebitda,
                                          '{:,.2f}'.format(amount_inputted),
                                          tax_rate_ebitda, '{:,.2f}'.format(loss_inputted), '{:,.2f}'.format(float(pbi_euro)), '{:,.2f}'.format(float(interest_euro))]
                        rows1.append({
                            columns[i]['id']: results_ebitda[i] for i in range(0, len(ebitda_df.columns))
                        })
    return rows1


# store datatable values
@dash_app.callback(
    Output('ebitda_table_store', 'data'),
    Input('ebitda_table', 'data'),
    Input('ebitda_table', 'columns')
)
def return_ebitda(data, columns):
    num_rows = len(data)
    groups1 = [''] * num_rows
    companies1 = [''] * num_rows
    interest_types1 = [''] * num_rows
    amounts1 = [''] * num_rows
    tax_rates1 = [''] * num_rows
    losses1 = [''] * num_rows
    pbie1 = [''] * num_rows
    deductint = [''] * num_rows

    for (i, row) in zip(range(0, num_rows), data):
        groups1[i] = row['Group']
        companies1[i] = row['Company']
        interest_types1[i] = row['EBITDA Category']
        amounts1[i] = row['Amount (€)']
        tax_rates1[i] = row['Tax Rate (%)']
        losses1[i] = row['Loss (€)']
        pbie1[i] = row['PBIE (€)']
        deductint[i] = row['Deductible Interest (€)']
    store_data = {'Group': groups1, 'Company': companies1, 'EBITDA Category': interest_types1,
                  'Amount (€)': amounts1, 'Tax Rate (%)': tax_rates1, 'Loss (€)': losses1,
                  'PBIE (€)': pbie1, 'Deductible Interest (€)': deductint}
    datalist1 = [{'ebitda_table_data': store_data}]
    return datalist1


##----------CLEARING FIELDS CALLBACKS-------------
# clearing data for additional companies and interest groups
@dash_app.callback(
    Output('group_name_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('company_name_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('interest_group_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('amount_input_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('tax_rate_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('input_loss_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('input_pbipp_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('input_deduct_ebitda', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return ''


@dash_app.callback(
    Output('ebitda_loss_toggle_switch', 'value'),
    Input('save_tax_ebitda', 'n_clicks')
)
def clear_output(n_clicks):
    if n_clicks > 0:
        return False


##----- spot rate callback ---------------------

@dash_app.callback(
    Output('ebitda_spot_rate_input', 'style'),
    Input('ebitda_currency_dd', 'value')
)
def show_hide_element(currency):
    if currency == 'USD ($)':
        return {'display': 'block', 'width': '80%'}
    elif currency == 'Euro (€)':
        return {'display': 'none'}
    else:
        return {'display': 'none'}


##-------converting & displaying amount in euro callback ------------

@dash_app.callback(
    Output('ebitda_amount_in_euro_text', 'style'),
    Input('spot_rate_store', 'data'),
    # Input('ebitda_currency_dd', 'value'),
    Input('amount_input_ebitda', 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'USD ($)' and amount != None:
            return {'display': 'block'}
        if currency == 'GBP (£)' and amount != None:
            return {'display': 'block'}
        if currency == 'Other' and amount != None:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_amount_in_euro_text', 'children'),
    Input('spot_rate_store', 'data'),
    Input('amount_input_ebitda', 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            if spot_rate != "No Spot Rate Entered":
                return "Amount in €: "
            else:
                return "Please enter spot rate"


@dash_app.callback(
    Output('ebitda_amount_in_euro_value', 'style'),
    Input('spot_rate_store', 'data'),
    Input('amount_input_ebitda', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency != 'Euro (€)' and amount != None and amount != '':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_amount_in_euro_value', 'children'),
    Input('spot_rate_store', 'data'),
    Input('amount_input_ebitda', 'value'),

)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            try:
                float(spot_rate)
                value = float(float(amount) / float(spot_rate))
                return '{:,.2f}'.format(value)
                #return round(float(float(amount) / float(spot_rate)), 2)
            except ValueError:
                return ""


##-------------loss-----------------------------
@dash_app.callback(
    Output('ebitda_loss_in_euro_text', 'style'),
    Input('spot_rate_store', 'data'),
    Input('input_loss_ebitda', 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'USD ($)' and amount != None:
            return {'display': 'block'}
        if currency == 'GBP (£)' and amount != None:
            return {'display': 'block'}
        if currency == 'Other' and amount != None:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_loss_in_euro_text', 'children'),
    Input('spot_rate_store', 'data'),
    Input('input_loss_ebitda', 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            if spot_rate != "No Spot Rate Entered":
                return "Amount in €: "
            else:
                return "Please enter spot rate"


@dash_app.callback(
    Output('ebitda_loss_in_euro_value', 'style'),
    Input('spot_rate_store', 'data'),
    Input('input_loss_ebitda', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency != 'Euro (€)' and amount != None and amount != '':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_loss_in_euro_value', 'children'),
    Input('spot_rate_store', 'data'),
    Input('input_loss_ebitda', 'value'),
    # Input('ebitda_spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            try:
                float(spot_rate)
                return round(float(float(amount) / float(spot_rate)), 2)
            except ValueError:
                return ""


##--------------adjusting names to go with currencies-----------------

@dash_app.callback(
    Output('ebitda_amount_description', 'children'),
    Input('spot_rate_store', 'data')
)
def change_text(spot_rate_store):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'Euro (€)':
            return html.H6("Amount (€)")
        else:
            if currency == 'GBP (£)':
                return html.H6("Amount (£)")
            elif currency == 'USD ($)':
                return html.H6("Amount ($)")
            else:
                return html.H6("Amount")
    else:
        return html.H6("Amount (€)")


@dash_app.callback(
    Output('ebitda_pbi_description', 'children'),
    Input('spot_rate_store', 'data')
)
def change_text(spot_rate_store):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'Euro (€)':
            return html.H6("Public Benefit Infrastructure (€)")
        else:
            if currency == 'USD ($)':
                return html.H6("Public Benefit Infrastructure ($)")
            elif currency == 'GBP (£)':
                return html.H6("Public Benefit Infrastructure (£)")
            else:
                return html.H6("Public Benefit Infrastructure")
    else:
        return html.H6("Public Benefit Infrastructure (€)")


@dash_app.callback(
    Output('ebitda_pbi_ded_description', 'children'),
    Input('spot_rate_store', 'data')
)
def change_text(spot_rate_store):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'Euro (€)':
            return html.H6("PBI Deductible Interest (€)")
        else:
            if currency == 'USD ($)':
                return html.H6("PBI Deductible Interest ($)")
            elif currency == 'GBP (£)':
                return html.H6("PBI Deductible Interest (£)")
            else:
                return html.H6("PBI Deductible Interest")
    else:
        return html.H6("PBI Deductible Interest (€)")


##-------converting & displaying PBI amount in euro callback ------------

@dash_app.callback(
    Output('ebitda_pbi_amount_in_euro_text', 'style'),
    Input('spot_rate_store', 'data'),
    Input("input_pbipp_ebitda", 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'USD ($)' and amount != None:
            return {'display': 'block'}
        if currency == 'GBP (£)' and amount != None:
            return {'display': 'block'}
        if currency == 'Other' and amount != None:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_pbi_amount_in_euro_text', 'children'),
    Input('spot_rate_store', 'data'),
    Input("input_pbipp_ebitda", 'value'),
    # Input('ebitda_spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            if spot_rate != "No Spot Rate Entered":
                return "Amount in €: "
            else:
                return "Please enter spot rate"


@dash_app.callback(
    Output('ebitda_pbi_amount_in_euro_value', 'style'),
    Input('spot_rate_store', 'data'),
    Input("input_pbipp_ebitda", 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency != 'Euro (€)' and amount != None and amount != '':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_pbi_amount_in_euro_value', 'children'),
    Input('spot_rate_store', 'data'),
    Input("input_pbipp_ebitda", 'value'),
    # Input('ebitda_spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            try:
                float(spot_rate)
                value = float(float(amount) / float(spot_rate))
                return '{:,.2f}'.format(value)
                #return round(float(float(amount) / float(spot_rate)), 2)
            except ValueError:
                return ""


##-----------deductible interest------------------
@dash_app.callback(
    Output('ebitda_pbi_interest_amount_in_euro_text', 'style'),
    Input('spot_rate_store', 'data'),
    Input("input_deduct_ebitda", 'value'),
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency == 'USD ($)' and amount != None:
            return {'display': 'block'}
        if currency == 'GBP (£)' and amount != None:
            return {'display': 'block'}
        if currency == 'Other' and amount != None:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_pbi_interest_amount_in_euro_text', 'children'),
    Input('spot_rate_store', 'data'),
    Input("input_deduct_ebitda", 'value'),
    # Input('ebitda_spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            if spot_rate != "No Spot Rate Entered":
                return "Amount in €: "
            else:
                return "Please enter spot rate"


@dash_app.callback(
    Output('ebitda_pbi_interest_amount_in_euro_value', 'style'),
    Input('spot_rate_store', 'data'),
    Input("input_deduct_ebitda", 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        if currency != 'Euro (€)' and amount != None and amount != '':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('ebitda_pbi_interest_amount_in_euro_value', 'children'),
    Input('spot_rate_store', 'data'),
    Input("input_deduct_ebitda", 'value'),
    # Input('ebitda_spot_rate_input', 'value')
)
def show_hide_element(spot_rate_store, amount):
    if spot_rate_store != [{}]:
        details = spot_rate_store[0]
        currency = details['currency']
        spot_rate = details['spot_rate']
        if currency != 'Euro (€)' and amount != None and amount != '':
            try:
                float(spot_rate)
                value = float(float(amount) / float(spot_rate))
                return '{:,.2f}'.format(value)
                #return round(float(float(amount) / float(spot_rate)), 2)
            except ValueError:
                return ""


## ------------------------ Calculations Callbacks--------------------

## ------------GETTING EBC CALLBACK-------------------------
@dash_app.callback(Output(component_id='tax_ebc_output', component_property='children'),
                   Input(component_id='tax_ebc', component_property='n_clicks'),
                   State('ebc_store', 'data')
                   )
def borrowing_costs(n_clicks, ebc):
    if n_clicks > 0:
        ebc_dict = ebc[0]
        return ebc_dict['ebc']


##-------------GETTING LEGACY DEBT CALLBACK----------------
@dash_app.callback(Output(component_id='tax_debt_output', component_property='children'),
                   Input(component_id='tax_debt', component_property='n_clicks'),
                   State('ebc_store_intcalc', 'data')
                   )
def legacy_debt(n_clicks, data):
    if n_clicks > 0:
        debt_dict = data[0]
        return '€{:,.2f}'.format(debt_dict['intcalc'])


##-------------workings company dropdown-----
@dash_app.callback(
    Output('ebitda_company_workings_dd', 'options'),
    Output('ebitda_company_workings_dd', 'value'),
    Input('ebitda_table', 'data'),
    State('ebc_store', 'data'),
    State('ebc_store_intcalc', 'data')
)
def company_dropdown(data, ebc_store, legacy_store):
    num_rows = len(data)
    if num_rows == 0:
        if len(ebc_store) == 1:
            if len(legacy_store) == 1:
                companies = ['No Companies Entered']
                options = [{'label': cmpy, 'value': cmpy} for cmpy in companies]
                value = companies[0]
                return options, value
            else:
                companies = []
                for dict in legacy_store:
                    companies = companies + [dict['Company']]
                options = [{'label': cmpy, 'value': cmpy} for cmpy in companies]
                value = companies[0]
                return options, value
        else:
            companies_init = ['All']
            companies1 = []
            companies2 = []
            for dict in ebc_store:
                if dict['Company'] != 'All':
                    companies1 = companies1 + [dict['Company']]
            for dict in legacy_store:
                if dict['Company'] != 'All':
                    companies2 = companies2 + [dict['Company']]
            companies4 = companies1 + companies2
            companies3 = sorted(list(set(companies4)))
            companies = companies_init + companies3
            options = [{'label': cmpy, 'value': cmpy} for cmpy in companies]
            value = companies[0]
            return options, value
    else:
        companies_init = ['All']
        companies1 = [None] * num_rows
        for (i, row) in zip(range(0, num_rows), data):
            companies1[i] = row['Company']

        companies_ebc = []
        companies_legacy = []
        for dict in ebc_store:
            if dict['Company'] != 'All':
                companies_ebc = companies_ebc + [dict['Company']]
        for dict in legacy_store:
            if dict['Company'] != 'All':
                companies_legacy = companies_legacy + [dict['Company']]
        companies2 = sorted(list(set(companies1 + companies_ebc + companies_legacy)))
        companies = companies_init + companies2
        options = [{'label': cmpy, 'value': cmpy} for cmpy in companies]
        value = companies[0]
        return options, value


##-------------TAX EBITDA CALCULATION CALLBACK--------------
def handling_inputs_ebc(data_list: list, dictkey: str) -> float:
    """
    Function to handle the inputs from ebc. It removes the unwanted characters and return an integer value.

    :param dictkey: string containing the dictionary key
    :param data_list: list containing a dictionary having values
    :return: values from ebc in float format
    """
    data_dict = data_list[0]

    if type(data_dict[dictkey]) == str:

        if not data_dict or data_dict[dictkey] == 'Not yet calculated':
            val = 0.0
        else:
            val = float(data_dict[dictkey][1:].replace(",", ""))
    else:
        if not data_dict or data_dict[dictkey] == 'Not yet calculated':
            val = 0.0
        else:
            val = float(data_dict[dictkey])
    return val


def handling_inputs_ebc_company(data_list: list, dictkey: str, company_entered) -> float:
    """
    Function to handle the inputs from ebc. It removes the unwanted characters and return an integer value.

    :param dictkey: string containing the dictionary key
    :param data_list: list containing a dictionary having values
    :return: values from ebc in float format
    """
    #   data_dict = data_list[0]
    val = 0
    for data_dict in data_list:
        if data_dict['Company'] == company_entered:
            if type(data_dict[dictkey]) == str:
                if not data_dict or data_dict[dictkey] == 'Not yet calculated':
                    val = 0.0
                else:
                    val = float(data_dict[dictkey][1:].replace(",", ""))
            else:
                if not data_dict or data_dict[dictkey] == 'Not yet calculated':
                    val = 0.0
                else:
                    val = float(data_dict[dictkey])
    return val


@dash_app.callback(Output('tax_ebitda_output', 'children'),
                   # Input('tax_ebitda', 'n_clicks'),
                   Input('ebitda_table', 'data'),
                   State('ebc_store', 'data'),
                   State('ebc_store_intcalc', 'data')
                   )
def calculate_tax_ebitda(data: list, ebc_dict: list, debt_dict: list) -> str:
    """
    Function to calculate the tax ebitda by taking all the components and generating the result.

    :param n_clicks: integer
    :param data: list containing tax_ebitda data.
    :param ebc_dict: list containing dictionary of borrowing cost data.
    :param debt_dict: list containing dictionary of legacy debt cost.
    :return: string containing the final tax ebitda.
    """
    num_rows = len(data)
    if num_rows == 0:
        if ebc_dict == [{}]:
            return "Not yet calculated"
        else:
            # if debt_dict == [{}]:
            borrowing_cost = handling_inputs_ebc(ebc_dict, 'ebc')
            legacy_debt_cost = handling_inputs_ebc(debt_dict, 'intcalc')
            tax_Ebitda = borrowing_cost + legacy_debt_cost
            return '€{:,.2f}'.format(tax_Ebitda)

    else:
        sum_taxable_profit = sum_foreign_tax = sum_capital_allow \
            = sum_deduct_finances = sum_balance_charges = 0.0
        borrowing_cost = handling_inputs_ebc(ebc_dict, 'ebc')
        legacy_debt_cost = handling_inputs_ebc(debt_dict, 'intcalc')

        # Tax EBITDA calculation
        for row in data:
            if row['EBITDA Category'] == "Relevant Profits (Taxable Profits)":
                sum_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
                             * float(row['Tax Rate (%)']) / corporate_tax
                sum_taxable_profit = sum_taxable_profit + sum_profit
            elif row['EBITDA Category'] == "Relevant Profits - Credit adjustment":
                sum_profit = (float(row['Amount (€)']) - float(row['PBIE (€)'])) \
                             * float(row['Tax Rate (%)']) / corporate_tax
                sum_taxable_profit = sum_taxable_profit + sum_profit
            elif row['EBITDA Category'] == "Foreign Tax Deductions":
                sum_foreign = (float(row['Amount (€)']) * float(row['Tax Rate (%)'])) / corporate_tax
                sum_foreign_tax = sum_foreign_tax + sum_foreign
            elif row['EBITDA Category'] == "Capital Allowances":
                sum_allowance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                * float(row['Tax Rate (%)']) / corporate_tax
                sum_capital_allow = sum_capital_allow + sum_allowance
            elif row['EBITDA Category'] == "Capital Element Of Deductible Finance Lease Payment":
                sum_deduct = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                sum_deduct_finances = sum_deduct_finances + sum_deduct
            elif row['EBITDA Category'] == "Balancing Charges":
                sum_balance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                              * float(row['Tax Rate (%)']) / corporate_tax
                sum_balance_charges = sum_balance_charges + sum_balance
            else:
                continue
        tax_ebitda = sum_taxable_profit + sum_foreign_tax + sum_capital_allow - sum_balance_charges + \
                     sum_deduct_finances + borrowing_cost + legacy_debt_cost
        return '€{:,.2f}'.format(tax_ebitda)


##-------------TAX EBITDA WORKINGS CALLBACK-----------------

@dash_app.callback(Output('ebitda_workings_output', 'children'),
                   Input('ebitda_table', 'data'),
                   Input('ebitda_company_workings_dd', 'value'),
                   State('ebc_store', 'data'),
                   State('ebc_store_intcalc', 'data')
                   
                   )
def ebitda_workings(data, ebc_dict, debt_dict, company_selected):
    num_rows = len(data)
    if num_rows == 0:
        if len(ebc_dict) > 1 or len(debt_dict) > 1:
            borrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', company_selected)
            legacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', company_selected)
            tax_ebitda_total = borrowing_cost + legacy_debt_cost
            formatted_tot_sum1 = '€{:,.2f}'.format(tax_ebitda_total)
            workings1 = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div('Relevant profit: ', style={'font-size': '80%'}),
                        html.Div('ADD Foreign tax deduction: ', style={'font-size': '80%'}),
                        html.Div('ADD Exceeding borrowing costs: ', style={'font-size': '80%'}),
                        html.Div('ADD Capital allowances: ', style={'font-size': '80%'}),
                        html.Div('ADD Capital element of deductible finance: ', style={'font-size': '80%'}),
                        html.Div('LESS Balancing charges: ', style={'font-size': '80%'}),
                        html.Div('ADD Legacy debt: ', style={'font-size': '80%'}),
                        html.Div('=', style={'font-size': '80%'})
                    ], width=6),

                    dbc.Col([
                        html.Div('€0.00', style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€0.00', style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(borrowing_cost), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€0.00', style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€0.00', style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€0.00', style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.U('€{:,.2f}'.format(legacy_debt_cost)),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.B('{}'.format(formatted_tot_sum1)),
                                 style={'text-align': 'right', 'font-size': '80%'})
                    ], width=2)
                ])

            ])
            return workings1

    else:
        sum_taxable_profit = sum_foreign_tax = sum_capital_allow = \
            sum_deduct_finances = sum_balance_charges = 0.0
        if company_selected == 'All' or company_selected == '' or company_selected is None:
            borrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', 'All')
            legacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', 'All')
            for row in data:
                if row['EBITDA Category'] == "Relevant Profits (Taxable Profits)":
                    sum_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
                                 * float(row['Tax Rate (%)']) / corporate_tax
                    sum_taxable_profit = sum_taxable_profit + sum_profit
                elif row['EBITDA Category'] == "Relevant Profits - Credit adjustment":
                    sum_profit = (float(row['Amount (€)']) - float(row['PBIE (€)'])) \
                                 * float(row['Tax Rate (%)']) / corporate_tax
                    sum_taxable_profit = sum_taxable_profit + sum_profit

                elif (row['EBITDA Category'] == "Relevant Profits (Taxable Profits)") or \
                        (row['EBITDA Category'] == "Relevant Profits - Credit adjustment"):
                    sum_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
                                 * float(row['Tax Rate (%)']) / corporate_tax
                    sum_taxable_profit = sum_taxable_profit + sum_profit

                elif row['EBITDA Category'] == "Foreign Tax Deductions":
                    sum_foreign = (float(row['Amount (€)']) * float(row['Tax Rate (%)'])) / corporate_tax
                    sum_foreign_tax = sum_foreign_tax + sum_foreign

                elif row['EBITDA Category'] == "Capital Allowances":
                    sum_allowance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                    * float(row['Tax Rate (%)']) / corporate_tax
                    sum_capital_allow = sum_capital_allow + sum_allowance

                elif row['EBITDA Category'] == "Capital Element Of Deductible Finance Lease Payment":
                    sum_deduct = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                    sum_deduct_finances = sum_deduct_finances + sum_deduct

                elif row['EBITDA Category'] == "Balancing Charges":
                    sum_balance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                  * float(row['Tax Rate (%)']) / corporate_tax
                    sum_balance_charges = sum_balance_charges + sum_balance
                else:
                    continue
            tax_ebitda_total = sum_taxable_profit + sum_foreign_tax + sum_capital_allow - sum_balance_charges + \
                               sum_deduct_finances + borrowing_cost + legacy_debt_cost
            formatted_tot_sum1 = '€{:,.2f}'.format(tax_ebitda_total)
            workings1 = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div('Relevant profit: ', style={'font-size': '80%'}),
                        html.Div('ADD Foreign tax deduction: ', style={'font-size': '80%'}),
                        html.Div('ADD Exceeding borrowing costs: ', style={'font-size': '80%'}),
                        html.Div('ADD Capital allowances: ', style={'font-size': '80%'}),
                        html.Div('ADD Capital element of deductible finance: ', style={'font-size': '80%'}),
                        html.Div('LESS Balancing charges: ', style={'font-size': '80%'}),
                        html.Div('ADD Legacy debt: ', style={'font-size': '80%'}),
                        html.Div('=', style={'font-size': '80%'})
                    ], width=6),

                    dbc.Col([
                        html.Div('€{:,.2f}'.format(sum_taxable_profit),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_foreign_tax), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(borrowing_cost), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_capital_allow),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_deduct_finances),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_balance_charges),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.U('€{:,.2f}'.format(legacy_debt_cost)),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.B('{}'.format(formatted_tot_sum1)),
                                 style={'text-align': 'right', 'font-size': '80%'})
                    ], width=2)
                ])

            ])
            return workings1

        else:
            borrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', company_selected)
            legacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', company_selected)
            for row in data:
                if row['Company'] == company_selected:
                    if row['EBITDA Category'] == "Relevant Profits (Taxable Profits)":
                        sum_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
                                     * float(row['Tax Rate (%)']) / corporate_tax
                        sum_taxable_profit = sum_taxable_profit + sum_profit
                    elif row['EBITDA Category'] == "Relevant Profits - Credit adjustment":
                        sum_profit = (float(row['Amount (€)']) - float(row['PBIE (€)'])) \
                                     * float(row['Tax Rate (%)']) / corporate_tax
                        sum_taxable_profit = sum_taxable_profit + sum_profit

                    elif (row['EBITDA Category'] == "Relevant Profits (Taxable Profits)") or \
                            (row['EBITDA Category'] == "Relevant Profits - Credit adjustment"):
                        sum_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
                                     * float(row['Tax Rate (%)']) / corporate_tax
                        sum_taxable_profit = sum_taxable_profit + sum_profit

                    elif row['EBITDA Category'] == "Foreign Tax Deductions":
                        sum_foreign = (float(row['Amount (€)']) * float(row['Tax Rate (%)'])) / corporate_tax
                        sum_foreign_tax = sum_foreign_tax + sum_foreign

                    elif row['EBITDA Category'] == "Capital Allowances":
                        sum_allowance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                        * float(row['Tax Rate (%)']) / corporate_tax
                        sum_capital_allow = sum_capital_allow + sum_allowance

                    elif row['EBITDA Category'] == "Capital Element Of Deductible Finance Lease Payment":
                        sum_deduct = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                        sum_deduct_finances = sum_deduct_finances + sum_deduct

                    elif row['EBITDA Category'] == "Balancing Charges":
                        sum_balance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                      * float(row['Tax Rate (%)']) / corporate_tax
                        sum_balance_charges = sum_balance_charges + sum_balance
                    else:
                        continue
            tax_ebitda_total = sum_taxable_profit + sum_foreign_tax + sum_capital_allow - sum_balance_charges + \
                               sum_deduct_finances + borrowing_cost + legacy_debt_cost
            formatted_tot_sum1 = '€{:,.2f}'.format(tax_ebitda_total)
            workings1 = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div('Relevant profit: ', style={'font-size': '80%'}),
                        html.Div('ADD Foreign tax deduction: ', style={'font-size': '80%'}),
                        html.Div('ADD Exceeding borrowing costs: ', style={'font-size': '80%'}),
                        html.Div('ADD Capital allowances: ', style={'font-size': '80%'}),
                        html.Div('ADD Capital element of deductible finance: ', style={'font-size': '80%'}),
                        html.Div('LESS Balancing charges: ', style={'font-size': '80%'}),
                        html.Div('ADD Legacy debt: ', style={'font-size': '80%'}),
                        html.Div('=', style={'font-size': '80%'})
                    ], width=6),

                    dbc.Col([
                        html.Div('€{:,.2f}'.format(sum_taxable_profit),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_foreign_tax), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(borrowing_cost), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_capital_allow),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_deduct_finances),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('€{:,.2f}'.format(sum_balance_charges),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.U('€{:,.2f}'.format(legacy_debt_cost)),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.B('{}'.format(formatted_tot_sum1)),
                                 style={'text-align': 'right', 'font-size': '80%'})
                    ], width=2)
                ])

            ])
            return workings1


##---UPDATING GROUP DROPDOWN USING HOME DATA CALLBACK--------
@dash_app.callback(
    Output("group_name_ebitda", "options"),
    Input("home_store", "data"),
)
def update_group_dropdown(data):
    if data != [{}]:
        group_data = data[0]
        if group_data['group']:
            return [{"label": i, "value": i} for i in group_data['group']]
        else:
            return [{"label": "No Groups", "value": "No Groups"}]
    else:
        return [{'label': grp, "value": grp} for grp in group_dummy]


##---UPDATING COMPANY DROPDOWN USING HOME DATA CALLBACK--------
@dash_app.callback(
    Output("company_name_ebitda", "options"),
    Input("home_store", "data"),
)
def update_company_dropdown(data):
    if data != [{}]:
        company_data = data[1]
        if company_data['company']:
            return [{"label": i, "value": i} for i in company_data['company']]
        else:
            return [{"label": "No Company", "value": "No Company"}]
    else:
        return [{'label': cmp, "value": cmp} for cmp in company_dummy]


##-----TAX EBITDA STORE CALLBACK-----------------------

@dash_app.callback(
    Output('tax_ebitda_store', 'data'),
    Input('ebitda_results_table', 'data')
)
def return_ebitda(data):
    datalist = []

    if data is None:
        datalist = [{'Company': 'All', 'Group': 'All', 'tax_ebitda': 'No Details Entered'}]
        return datalist

    else:
        num_rows = len(data)

        if num_rows == 0:
            datalist = [{'Company': 'All', 'Group': 'All', 'tax_ebitda': 'No Details Entered'}]
            return datalist

        if num_rows > 0:
            company_list1 = []
            for row in data:
                if row['Company'] != 'Group Total':
                    company_list1 = company_list1 + [row['Company']]
            company_list = sorted(list(set(company_list1)))

            for row in data:
                if row['Company'] == 'Group Total':
                    tax_ebitda = row['Tax EBITDA']
                    datalist = datalist + [{'Company': 'All', 'Group': 'All', 'tax_ebitda': '€{}'.format(tax_ebitda)}]

            for company in company_list:
                for row in data:
                    if row['Company'] == company:
                        group = row['Group']
                        tax_ebitda = row['Tax EBITDA']
                        datalist = datalist + [
                            {'Company': company, 'Group': group, 'tax_ebitda': '€{}'.format(tax_ebitda)}]

            return datalist


#  Limitation spare capacity

##-----LIMITATION SPARE CAPACITY STORE CALLBACK---------

@dash_app.callback(
    Output('tax_ebitda_store_lim_spare_cap', 'data'),
    Input('ebitda_table', 'data'),
    State('ebc_store', 'data')
)
def return_lim_spar_cap(data, ebc_dict):
    if data is None:
        datalist = [{'Company': 'All', 'Group': 'All', 'limit_spare_capacity': 0}]
        return datalist
    else:
        num_rows = len(data)
        if num_rows == 0:
            datalist = []
            for dict in ebc_dict:
                datalist = datalist + [{'Company': dict['Company'], 'Group': dict['Group'], 'limit_spare_capacity': 0}]
        else:
            ebc_companies = []
            tax_companies1 = []
            for dict in ebc_dict:
                if dict['Company'] != 'All':
                    ebc_companies = ebc_companies + [dict['Company']]
            for row in data:
                tax_companies1 = tax_companies1 + [row['Company']]
            tax_companies = sorted(list(set(tax_companies1)))

            all_companies1 = ebc_companies + tax_companies
            all_companies = sorted(list(set(all_companies1)))
            # if n_clicks != 0:
            lim_spare_cap = 0
            for row in data:
                if row['EBITDA Category'] == "Limitation Spare Capacity Carried Forward":
                    lim_spare_cap = lim_spare_cap + float(row['Amount (€)'])
            datalist = [{'Company': 'All', 'Group': 'All', 'limit_spare_capacity': lim_spare_cap}]

            for company in all_companies:
                # only in ebc
                if company not in tax_companies:
                    for dict in ebc_dict:
                        if dict['Company'] == company:
                            group = dict['Group']
                    datalist = datalist + [{'Company': company, 'Group': group, 'limit_spare_capacity': 0}]
                else:
                    comp_lim_spare_cap = 0
                    for row in data:
                        if row['Company'] == company:
                            group = row['Group']
                            if row['EBITDA Category'] == "Limitation Spare Capacity Carried Forward":
                                comp_lim_spare_cap = comp_lim_spare_cap + float(row['Amount (€)'])
                    datalist = datalist + [
                        {'Company': company, 'Group': group, 'limit_spare_capacity': comp_lim_spare_cap}]

        return datalist


##--------------Results table callback------------------------
@dash_app.callback(Output('ebitda_results_table', 'data'),
                   Input('ebitda_table', 'data'),
                   State('ebitda_results_table', 'columns'),
                   State('ebc_store', 'data'),
                   State('ebc_store_intcalc', 'data')
                   )
def ebitda_calc(inputted_data, results_columns, ebc_dict, debt_dict):
    # print(ebc_dict)
    num_rows = len(inputted_data)
    if num_rows == 0:
        if len(ebc_dict) > 1 or len(debt_dict) > 1:
            results_data = []
            for dict in ebc_dict:
                company = dict['Company']
                if company != 'All':
                    group = dict['Group']
                    borrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', company)
                    legacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', company)
                    tax_ebitda = borrowing_cost + legacy_debt_cost
                    company_result = [group, company, '{:,.2f}'.format(tax_ebitda)]
                    results_data.append({
                        results_columns[j]['id']: company_result[j] for j in range(0, len(company_result))
                    })

            group_list = []
            for dict in ebc_dict:
                if dict['Group'] != 'All':
                    group_list = group_list + [dict['Group']]
            groups = sorted(list(set(group_list)))

            # handling group feature?
            for group in groups:
                gtax_ebitda = 0
                for dict in ebc_dict:
                    if dict['Group'] == group:
                        company = dict['Company']
                        borrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', company)
                        legacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', company)
                        gtax_ebitda = gtax_ebitda + borrowing_cost + legacy_debt_cost
                group_result = [group, 'Group Total', '{:,.2f}'.format(gtax_ebitda)]
                results_data.append({
                    results_columns[j]['id']: group_result[j] for j in range(0, len(group_result))
                })

            return results_data

    if num_rows > 0:
        results_data = []

        # get list of companies
        company_list1 = [None] * num_rows
        for (i, row) in zip(range(0, num_rows), inputted_data):
            company_list1[i] = row['Company']

        company_list2 = []
        for dict in ebc_dict:
            if dict['Company'] != 'All':
                company_list2 = company_list2 + [dict['Company']]

        company_list3 = []
        for dict in debt_dict:
            if dict['Company'] != 'All':
                company_list3 = company_list3 + [dict['Company']]

        company_list4 = company_list1 + company_list2 + company_list3
        company_list = sorted(list(set(company_list4)))

        for company in company_list:
            # getting groups - company has EBC entry
            if company in company_list2:
                for dict in ebc_dict:
                    if dict['Company'] == company:
                        group = dict['Group']
            else:
                for row in inputted_data:
                    if row['Company'] == company:
                        group = row['Group']

            borrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', str(company))
            legacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', str(company))
            sum_taxable_profit = sum_foreign_tax = sum_capital_allow \
                = sum_deduct_finances = sum_balance_charges = 0.0
            for row in inputted_data:
                if row['Company'] == company:
                    # group = row['Group']
                    if row['EBITDA Category'] == "Relevant Profits (Taxable Profits)":
                        sum_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
                                     * float(row['Tax Rate (%)']) / corporate_tax
                        sum_taxable_profit = sum_taxable_profit + sum_profit
                    elif row['EBITDA Category'] == "Relevant Profits - Credit adjustment":
                        sum_profit = (float(row['Amount (€)']) - float(row['PBIE (€)'])) \
                                     * float(row['Tax Rate (%)']) / corporate_tax
                        sum_taxable_profit = sum_taxable_profit + sum_profit
                    elif row['EBITDA Category'] == "Foreign Tax Deductions":
                        sum_foreign = (float(row['Amount (€)']) * float(row['Tax Rate (%)'])) / corporate_tax
                        sum_foreign_tax = sum_foreign_tax + sum_foreign
                    elif row['EBITDA Category'] == "Capital Allowances":
                        sum_allowance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                        * float(row['Tax Rate (%)']) / corporate_tax
                        sum_capital_allow = sum_capital_allow + sum_allowance
                    elif row['EBITDA Category'] == "Capital Element Of Deductible Finance Lease Payment":
                        sum_deduct = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                        sum_deduct_finances = sum_deduct_finances + sum_deduct
                    elif row['EBITDA Category'] == "Balancing Charges":
                        sum_balance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                      * float(row['Tax Rate (%)']) / corporate_tax
                        sum_balance_charges = sum_balance_charges + sum_balance
                    else:
                        continue
            tax_ebitda = sum_taxable_profit + sum_foreign_tax + sum_capital_allow - sum_balance_charges + \
                         sum_deduct_finances + borrowing_cost + legacy_debt_cost
            company_result = [group, company, '{:,.2f}'.format(tax_ebitda)]
            results_data.append({
                results_columns[j]['id']: company_result[j] for j in range(0, 3)
            })

        group_list1 = []
        for dict in ebc_dict:
            if dict['Group'] != 'All':
                group_list1 = group_list1 + [dict['Group']]

        group_list2 = []
        for row in inputted_data:
            group_list2 = group_list2 + [row['Group']]

        group_list3 = group_list1 + group_list2
        groups = sorted(list(set(group_list3)))

        for group in groups:
            gtax_ebitda = 0
            gborrowing_cost = 0
            glegacy_debt_cost = 0
            # gborrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', 'All')
            # glegacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', 'All')
            gsum_profit = 0
            gsum_taxable_profit = 0
            gsum_credit_profit = 0
            gsum_foreign = 0
            gsum_foreign_tax = 0
            gsum_allowance = 0
            gsum_capital_allow = 0
            gsum_deduct_finances = 0
            gsum_deduct = 0
            gsum_balance = 0
            gsum_balance_charges = 0
            gborrowing_cost = 0
            glegacy_debt_cost = 0

            for dict in ebc_dict:
                if dict['Group'] == group:
                    if type(dict['ebc'])==str:
                        try:
                            float(dict['ebc'][1:].replace(",", ""))
                            gborrowing_cost = gborrowing_cost + float(dict['ebc'][1:].replace(",", ""))
                        except ValueError:
                            gborrowing_cost = gborrowing_cost
                    else:
                        if not dict or dict['ebc'] == 'Not yet calculated':
                            gborrowing_cost = gborrowing_cost
                        else:
                            gborrowing_cost = gborrowing_cost + float(dict['ebc'])
            
            # print(debt_dict)
            for dict in debt_dict:
                if dict['Group'] == group:
                    glegacy_debt_cost = glegacy_debt_cost + dict['intcalc']

            for row in inputted_data:
                if row['Group'] == group:
                    # company_borrowing_cost = handling_inputs_ebc_company(ebc_dict, 'ebc', row['Company'])
                    # gborrowing_cost = gborrowing_cost + company_borrowing_cost

                    # company_legacy_debt_cost = handling_inputs_ebc_company(debt_dict, 'intcalc', row['Company'])
                    # glegacy_debt_cost = glegacy_debt_cost + company_legacy_debt_cost

                    if row['EBITDA Category'] == "Relevant Profits (Taxable Profits)":
                        company_taxable_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
                                       * float(row['Tax Rate (%)']) / corporate_tax
                    else:
                        company_taxable_profit = 0
                    gsum_taxable_profit = gsum_taxable_profit + company_taxable_profit

                    if row['EBITDA Category'] == "Relevant Profits - Credit adjustment":
                        company_credit_profit =(float(row['Amount (€)']) - float(row['PBIE (€)'])) \
                                       * float(row['Tax Rate (%)']) / corporate_tax 
                    else:
                        company_credit_profit = 0
                    gsum_credit_profit = gsum_credit_profit + company_credit_profit

                    
                    if row['EBITDA Category'] == "Foreign Tax Deductions":
                        company_foreign_tax= (float(row['Amount (€)']) * float(row['Tax Rate (%)'])) / corporate_tax
                    else:
                        company_foreign_tax = 0
                    gsum_foreign_tax = gsum_foreign_tax + company_foreign_tax


                    if row['EBITDA Category'] == "Capital Allowances":
                        company_allowance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                          * float(row['Tax Rate (%)']) / corporate_tax
                    else:
                        company_allowance = 0
                    gsum_capital_allow = gsum_capital_allow + company_allowance

                    if row['EBITDA Category'] == "Capital Element Of Deductible Finance Lease Payment":
                        company_deduct = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
                    else:
                        company_deduct = 0
                    gsum_deduct_finances = gsum_deduct_finances + company_deduct

                    if row['EBITDA Category'] == "Balancing Charges":
                        company_balance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
                                        * float(row['Tax Rate (%)']) / corporate_tax
                    else:
                        company_balance = 0
                    gsum_balance_charges = gsum_balance_charges + company_balance


            #print(gsum_taxable_profit + gsum_credit_profit)
            print(gsum_credit_profit)
            # print(gsum_foreign_tax)
            # print(gborrowing_cost)
            # print(gsum_capital_allow)
            # print(gsum_deduct_finances)
            # print(gsum_balance_charges)
            # print(glegacy_debt_cost)
            gtax_ebitda = gsum_taxable_profit + gsum_credit_profit + gsum_foreign_tax + gborrowing_cost \
                + gsum_capital_allow + gsum_deduct_finances - gsum_balance_charges + glegacy_debt_cost
            group_result = [group, 'Group Total', '{:,.2f}'.format(gtax_ebitda)]
            results_data.append({
                 results_columns[j]['id']: group_result[j] for j in range(0, len(group_result))
             })

        return results_data    

        #     for row in inputted_data:                    
        #         # group = row['Group']
        #         if row['Group'] == group:
        #             company = row['Company']
        #             gborrowing_cost = gborrowing_cost + handling_inputs_ebc_company(ebc_dict, 'ebc', company)
        #             glegacy_debt_cost = glegacy_debt_cost + handling_inputs_ebc_company(debt_dict, 'intcalc', company)
        #             if row['EBITDA Category'] == "Relevant Profits (Taxable Profits)":
        #                 gsum_profit = (float(row['Amount (€)']) - float(row['Loss (€)']) - float(row['PBIE (€)'])) \
        #                               * float(row['Tax Rate (%)']) / corporate_tax
        #                 gsum_taxable_profit = gsum_taxable_profit + gsum_profit
        #                 print(gsum_taxable_profit)
        #             elif row['EBITDA Category'] == "Relevant Profits - Credit adjustment":
        #                 gsum_profit = (float(row['Amount (€)']) - float(row['PBIE (€)'])) \
        #                               * float(row['Tax Rate (%)']) / corporate_tax
        #                 gsum_taxable_profit = gsum_taxable_profit + gsum_profit
        #                 print(gsum_taxable_profit)
        #             elif row['EBITDA Category'] == "Foreign Tax Deductions":
        #                 gsum_foreign = (float(row['Amount (€)']) * float(row['Tax Rate (%)'])) / corporate_tax
        #                 gsum_foreign_tax = gsum_foreign_tax + gsum_foreign
        #                 print(gsum_foreign_tax)
        #             elif row['EBITDA Category'] == "Capital Allowances":
        #                 gsum_allowance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
        #                                  * float(row['Tax Rate (%)']) / corporate_tax
        #                 gsum_capital_allow = gsum_capital_allow + gsum_allowance
        #                 print(gsum_capital_allow)
        #             elif row['EBITDA Category'] == "Capital Element Of Deductible Finance Lease Payment":
        #                 gsum_deduct = float(row['Amount (€)']) * float(row['Tax Rate (%)']) / corporate_tax
        #                 gsum_deduct_finances = gsum_deduct_finances + gsum_deduct
        #                 print(gsum_deduct_finances)
        #             elif row['EBITDA Category'] == "Balancing Charges":
        #                 gsum_balance = (float(row['Amount (€)']) - float(row['Deductible Interest (€)'])) \
        #                                * float(row['Tax Rate (%)']) / corporate_tax
        #                 gsum_balance_charges = gsum_balance_charges + gsum_balance
        #                 print(gsum_balance_charges)
        #             else:
        #                 continue
        #         gtax_ebitda = gtax_ebitda + gsum_taxable_profit + gsum_foreign_tax + gsum_capital_allow - gsum_balance_charges + \
        #             gsum_deduct_finances + gborrowing_cost + glegacy_debt_cost
        #     group_result = [group, 'Group Total', '{:,.2f}'.format(gtax_ebitda)]
        #     results_data.append({
        #         results_columns[j]['id']: group_result[j] for j in range(0, len(group_result))
        #     })

        # return results_data


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------GROUP RATIO PAGE-------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##-------------------------------GROUP RATIO VARIABLES--------------------------


# current_year = datetime.datetime.today().year
# year = range(current_year, current_year - 10, -1)
tax_rates = [12.5, 25, 33, 'Other']
kpmgBlue_hash = '#00338D'

##-------------------------------GROUP RATIO LAYOUT--------------------------


# CREATING CARD WHERE USER INPUTS DETAILS
gr_card_question = dbc.Card(
    [
        dbc.CardBody([
            # title of card
            dbc.Row([
                dbc.Col([
                    html.Div([
                        
                        html.Div(html.H2("Group Ratio", className="card-title", style={'color': kpmgBlue_hash}), style={'display': 'inline-block'}),
                        
                        html.Div(html.I(id="popover-target4", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left':'10px', 'display': 'inline-block'})
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

gr_layout = html.Div([
    gr_card_question,
    html.P(""),
    gr_results_card,
    html.P(""),
    html.P("")
])


##-------------------------------GROUP RATIO CALLBACKS--------------------------


##--------GROUP RATIO CALCULATION CALLBACK--------

@dash_app.callback(Output('group_ratio_output', 'children'),
                   Input(component_id='inputA', component_property='value'),
                   Input(component_id='inputB', component_property='value'))
def get_group_ratio(inputA, inputB):
    if inputA is not None and inputB is not None:
        group_ratio = round(int(inputA) / int(inputB), 4)
        group_ratio_percent = round(int(inputA) / int(inputB), 4) * 100
        return "{}%".format(group_ratio_percent)
    else:
        return "Not calculated yet - Please enter details"


##--------GROUP RATIO STORE CALLBACK-------------
@dash_app.callback(
    Output('group_ratio_store', 'data'),
    Input('group_ratio_output', 'children')
)
def return_group_ratio(group_ratio_percent):
    if group_ratio_percent[-1] == "%":
        group_ratio = round(float(group_ratio_percent[:-1]) / 100, 4)
    else:
        group_ratio = group_ratio_percent
    data = [{'group_ratio': group_ratio}]
    return data


##--------------storing entries -------------------


@dash_app.callback(
    Output('group_ratio_workings', 'children'),
    Input('inputA', 'value'),
    Input('inputB', 'value')
)
def gr_workings(inputA, inputB):
    if inputA is None or inputB is None:
        workings = ''

    else:
        if inputA is None:
            # inputA_value = "Please Enter Details"
            inputA_value = ""
        else:
            inputA_value = str(inputA)

        if inputB is None:
            # inputB_value = "Please Enter Details"
            inputB_value = ""
        else:
            inputB_value = str(inputB)

        try:
            float(inputA_value) and float(inputB_value)
            value_final = round(float(inputA_value) / float(inputB_value), 4)
            value_final_pct = '{}%'.format(round(100 * value_final, 4))
        except ValueError:
            value_final = ''
            value_final_pct = ''

        workings = dbc.Row([
            dbc.Col([
                html.Div("Worldwide Group Net Finance Expense From Consolidated Financial Statements: ",
                         style={'font-size': '80%'}),
                html.Div("DIVIDED BY Worldwide Group EBITDA From Consolidated Financial Statements: ",
                         style={'font-size': '80%'}),
                html.Div("=", style={'font-size': '80%'}),
                html.Div("%", style={'font-size': '80%'}),
            ],
                width=6),

            dbc.Col([
                html.Div("{}".format(inputA_value), style={'text-align': 'right', 'font-size': '80%'}),
                html.Div(html.U("{}".format(inputB_value)), style={'text-align': 'right', 'font-size': '80%'}),
                html.Div("{}".format(value_final), style={'text-align': 'right', 'font-size': '80%'}),
                html.Div(html.B("{}".format(value_final_pct)), style={'text-align': 'right', 'font-size': '80%'}),
            ],
                width=2),
        ])

    return workings


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------EQUITY RATIO PAGE-------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##-------------------------------EQUITY RATIO VARIABLES--------------------------

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
                        
                        html.Div(html.I(id="popover-target5", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left':'10px', 'display': 'inline-block'})
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

er_layout = html.Div([
    er_card_question,
    html.P(""),
    er_results_card,
    html.P("")

])


##-------------------------------EQUITY RATIO CALLBACKS--------------------------


###---TOGGLE SWITCH COLOUR CALLBACKS---
# To make option selected by toggle switch bold and blue

@dash_app.callback(
    Output('eq_no', 'children'),
    Input('eq_toggle_switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6("No", style={'color': '#D4D4D4'})
    else:
        return html.H6(html.B("No"), style={'color': kpmgBlue_hash})


@dash_app.callback(
    Output('eq_yes', 'children'),
    Input('eq_toggle_switch', 'value')
)
def bold(switch):
    if switch:
        return html.H6(html.B("Yes"), style={'color': kpmgBlue_hash})
    else:
        return html.H6("Yes", style={'color': '#D4D4D4'})


# Hide Debt from associated enterprises Input box
@dash_app.callback(
    Output('debt_assoc_enterprise', 'style'),
    Input('eq_toggle_switch', 'value'),
)
def show_hide_element(toggle):
    if toggle:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@dash_app.callback(
    Output('debt_assoc_enterprise_title', 'style'),
    Input('eq_toggle_switch', 'value'),
)
def show_hide_element(toggle):
    if toggle:
        return {'display': 'block', 'font-size': '100%'}
    else:
        return {'display': 'none'}


##---------INTEREST EQUITY RATIO CALCULATION CALLBACK----------
@dash_app.callback([Output('er_outputA', 'children'), Output('equity_ratio_store_group', 'data')],
                   Input(component_id='inputE', component_property='value'),
                   Input(component_id='inputF', component_property='value'),
                   Input(component_id='eq_toggle_switch', component_property='value'),
                   Input(component_id='debt_assoc_enterprise', component_property='value')
                   )
def get_equity_ratio(inputE, inputF, toggle, debt):
    if toggle:
        if inputE is not None and inputF is not None and debt is not None:
            A_calc_percent = round((float(inputE) - float(debt)) / float(inputF), 5) * 100
            group = A_calc_percent / 100
            data = [{'group': group}]
            return ["{:.2f}%".format(A_calc_percent), data]
        else:
            data = [{'group': "Not calculated yet - Please enter details"}]
            return ["Not calculated yet - Please enter details", data]
    if not toggle:
        if inputE is not None and inputF is not None:
            A_calc_percent = round((float(inputE)) / float(inputF), 5) * 100
            group = A_calc_percent / 100
            data = [{'group': group}]
            return ["{:.2f}%".format(A_calc_percent), data]
        else:
            data = [{'group': "Not calculated yet - Please enter details"}]
            return ["Not calculated yet - Please enter details", data]


##---------INTEREST EQUITY RATIO WORKINGS CALLBACK----------
# workings
@dash_app.callback(Output('er_workingsA', 'children'),
                   Input(component_id='inputE', component_property='value'),
                   Input(component_id='inputF', component_property='value'),
                   Input(component_id='eq_toggle_switch', component_property='value'),
                   Input(component_id='debt_assoc_enterprise', component_property='value')
                   )
def get_equity_ratio(inputE, inputF, toggle, debt):
    if toggle == True:
        if inputE is not None and inputF is not None and debt is not None:
            A_calc = (float(inputE) - float(debt)) / float(inputF)
            A_calc_percent = round(A_calc, 5) * 100

            workings = html.Div([
                dbc.Row([

                    dbc.Col([
                        html.Div('As Single Company Worldwide Group', style={'font-size': '80%'}),
                        html.Div('Interest Group Equity: ', style={'font-size': '80%'}),
                        html.Div('LESS Debt from Associated Enterprises: ', style={'font-size': '80%'}),
                        html.Div('DIVIDED BY Interest Group Total Assets: ', style={'font-size': '80%'}),
                        html.Div('=', style={'font-size': '80%'}),
                        html.Div('%', style={'font-size': '80%'}),
                    ], width=7),

                    dbc.Col([
                        html.Br(),
                        html.Div('{:,.2f} '.format(float(inputE)), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div('{:,.2f} '.format(float(debt)), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.U('{:,.2f}'.format(inputF)), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.B('{:,.2f} '.format(A_calc)), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.B('{:,.2f}% '.format(A_calc_percent)),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                    ], width=3),

                ])

            ])

            return workings

    if not toggle:
        if inputE is not None and inputF is not None:
            A_calc = float(inputE) / float(inputF)
            A_calc_percent = round((A_calc), 5) * 100

            workings = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div('As not Single Company Worldwide Group', style={'font-size': '80%'}),
                        html.Div('Interest Group Equity: ', style={'font-size': '80%'}),
                        html.Div('DIVIDED BY Interest Group Total Assets: ', style={'font-size': '80%'}),
                        html.Div('=', style={'font-size': '80%'}),
                        html.Div('%', style={'font-size': '80%'}),
                    ], width=7),

                    dbc.Col([
                        html.Br(),
                        html.Div('{:,.2f} '.format(float(inputE)), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.U('{:,.2f}'.format(inputF)), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.B('{:,.2f} '.format(A_calc)), style={'text-align': 'right', 'font-size': '80%'}),
                        html.Div(html.B('{:,.2f}% '.format(A_calc_percent)),
                                 style={'text-align': 'right', 'font-size': '80%'}),
                    ], width=3),

                ])

            ])
            return workings


##---------WORLDWIDE EQUITY RATIO CALCULATION CALLBACK----------
@dash_app.callback([Output('er_outputB', 'children'), Output('equity_ratio_store_worldwide', 'data')],
                   Input(component_id='inputC', component_property='value'),
                   Input(component_id='inputD', component_property='value'))
def get_equity_ratio(inputC, inputD):
    if inputC is not None and inputD is not None:
        B_calc_percent = round((float(inputC)) / float(inputD), 5) * 100
        worldwide = B_calc_percent / 100
        data = [{'worldwide': worldwide}]
        return ["{:.2f}%".format(B_calc_percent), data]
    else:
        data = [{'worldwide': "Not calculated yet - Please enter details"}]
        return ["Not calculated yet - Please enter details", data]


##---------WORLDWIDE EQUITY RATIO WORKINGS CALLBACK----------
# workings
@dash_app.callback(Output('er_workingsB', 'children'),
                   Input(component_id='inputC', component_property='value'),
                   Input(component_id='inputD', component_property='value'),
                   )
def get_equity_ratio(inputC, inputD):
    if inputC is not None and inputD is not None:
        B_calc = (float(inputC)) / float(inputD)
        B_calc_percent = round(B_calc, 5) * 100

        workings = html.Div([
            dbc.Row([

                dbc.Col([
                    html.Div('Worldwide Group Equity: ', style={'font-size': '80%'}),
                    html.Div('DIVIDED BY Worldwide Group Total Assets: ', style={'font-size': '80%'}),
                    html.Div('=', style={'font-size': '80%'}),
                    html.Div('%', style={'font-size': '80%'}),
                ], width=7),

                dbc.Col([
                    html.Div('{:,.2f} '.format(float(inputC)), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.U('{:,.2f}'.format(inputD)), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.B('{:,.2f} '.format(B_calc)), style={'text-align': 'right', 'font-size': '80%'}),
                    html.Div(html.B('{:,.2f}% '.format(B_calc_percent)),
                             style={'text-align': 'right', 'font-size': '80%'}),
                ], width=3),

            ])

        ])

        return workings


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------DISALLOWANCE PAGE-----------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


##-------------------------------DISALLOWANCE LAYOUT--------------------------

# card to test if disallowance is applied, which tests are passed etc
disallowance_card = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        
                        html.Div(html.H2("Disallowance Formula", className="card-title", style={'color': kpmgBlue_hash}), style={'display': 'inline-block'}),
                        
                        html.Div(html.I(id="popover-target6", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left':'10px', 'display': 'inline-block'})
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

disallowance_layout = html.Div([
    disallowance_card,
    html.P(""),
    disallowance_workings_card
]),


##-------------------------------DISALLOWANCE CALLBACKS--------------------------

##-------EQUITY RATIO TEST CALLBACK-------------------
@dash_app.callback(
    Output('within-output', 'children'),
    Input('equity_ratio_store_group', 'data'),
    Input('equity_ratio_store_worldwide', 'data')
)
def decisionmessage(ersg, ersw):
    if ersg == [{}] or ersw == [{}]:
        return html.H6("")
    # formatting
    else:
        groupvalDict = ersg[0]
        groupval = groupvalDict["group"]
        worldwidevalDict = ersw[0]
        worldwideval = worldwidevalDict["worldwide"]

        # logic test
        try:
            float(groupval) and float(worldwideval)
            value = round(worldwideval - groupval, 10)
            if value <= 0.02:
                return html.H6(html.B("Passes Equity Ratio: No disallowance applied"), style={'color': kpmgBlue_hash})
            elif value > 0.02:
                return html.H6(html.B("Fails Equity Ratio: Disallowance applied"), style={'color': kpmgBlue_hash})
            else:
                return html.H6("")

        except ValueError:
            return html.H6("")


##------WITHIN SCOPE CALLBACK-------------------------
@dash_app.callback(
    Output('scope-output', 'children'),
    Input('ebc_store_dm', 'data')
)
def decisionmessage(data):
    if data == [{}]:
        return html.H6("")
    else:
        ebc_dm = data[0]
        ebc_dm1 = ebc_dm["ebc_dm"][1:]
        ebc_dm2 = ebc_dm1.replace(',', '')
        try:
            float(ebc_dm2)
            value = float(ebc_dm2)
            if value > 3000000:
                return html.H6(html.B("Exceeds the De Minimis amount (€3m): Disallowance applied"),
                               style={'color': kpmgBlue_hash})
            elif value <= 3000000:
                return html.H6(html.B("Within the De Minimis amount (€3m): No disallowance applied"),
                               style={'color': kpmgBlue_hash})
            else:
                return html.H6("")
        except ValueError:
            return html.H6("")


##-----EBC SIGN CALLBACK-------------------------------

@dash_app.callback(
    Output('sign-output', 'children'),
    Input('ebc_store', 'data')
)
def decisionmessage(data):
    if data == [{}]:
        return html.H6("")
    else:
        ebc = data[0]
        ebc1 = ebc["ebc"][1:]
        ebc2 = ebc1.replace(',', '')
        try:
            float(ebc2)
            value = float(ebc2)
            if value > 0:
                return html.H6(html.B("Exceeding Borrowing Costs is positive"), style={'color': kpmgBlue_hash})
            elif value < 0:
                return html.H6(html.B("Exceeding Borrowing Costs is negative"), style={'color': kpmgBlue_hash})
            elif value == 0:
                return html.H6(html.B("Error: Exceeding Borrowing Costs is 0"), style={'color': kpmgBlue_hash})
            else:
                return html.H6("")
        except ValueError:
            return html.H6("")


# function to account for store formatting
def euroformatting(xUnformated, xKey, fail):
    ### Format EBC, strip € and commas from store
    xUnformated1 = xUnformated[0]
    xUnformated2 = xUnformated1[xKey][1:]
    xFormated = xUnformated2.replace(',', '')
    try:
        float(xFormated)
        x = float(xFormated)
    except ValueError:
        x = fail
    return x


def formatting(xDict, xKey, fail):
    xDictInd = xDict[0]
    xInd = xDictInd[xKey]
    try:
        float(xInd)
        x = float(xInd)
    except ValueError:
        x = fail
    return x


###---Disallowance Formula Calculation----

##-------DISALLOWANCE CALCULATION CALLBACK------------------
# ----------RESULTS IN TABLE---------------------------------
@dash_app.callback(
    Output('dis-output', 'children'),
    # Input('dis-calculate', 'n_clicks'),
    # Input('within-output', 'children'),
    # Input('sign-output', 'children'),
    Input('ebc_store', 'data'),
    Input('group_ratio_store', 'data'),
    Input('tax_ebitda_store', 'data'),
    Input('ebc_store_spareCap', 'data'),
    Input('ebc_store_intcalc', 'data'),
    Input('equity_ratio_store_group', 'data'),
    Input('equity_ratio_store_worldwide', 'data'),
    Input('tax_ebitda_store_lim_spare_cap', 'data')
)
### Limited Spare Capacity needed
def disallowanceformula(ebcPre, groupRatPre, ebitdaPre, iscPre, intcalcPre, erGroupPre, erWrldPre, lscPre):
    # if n_clicks > 0:
    # Call our formatting functions
    ebc = euroformatting(ebcPre, "ebc", 0)
    groupRat = formatting(groupRatPre, "group_ratio", 0)
    ebitda = euroformatting(ebitdaPre, "tax_ebitda", 0)
    isc = formatting(iscPre, "spare_capacity", 0)
    intcalc = formatting(intcalcPre, "intcalc", 0)

    erGroup = formatting(erGroupPre, "group", 0)
    erWrld = formatting(erWrldPre, "worldwide", 0)
    lsc = formatting(lscPre, "limit_spare_capacity", 0)

    # "Fails interest restrictions. Disallowance applied."
    if erGroup == 0 and erWrld == 0:
        workings = "Equity Ratio Test not completed yet"

    else:
        value = round(float(erWrld) - float(erGroup), 10)
        if value <= .02:
            workings = "Passes Interest restrictions: No disallowance applied"
        else:
            ### If EBC Positive, apply disallowance formula
            #### Disallowance and TotSpareCap returned (along with respective tax values)
            if ebc > 0:
                # Check if group ratio or 30% is greater
                if groupRat > 0.3:
                    disFormula = (groupRat * ebitda) + lsc + isc
                else:
                    disFormula = (0.3 * ebitda) + lsc + isc

                # Compare disallowance formula to EBC
                # Total Spare Capacity calculated here
                if disFormula < ebc:
                    disAmount = ebc - disFormula
                    totSpareCap = 0

                else:
                    disAmount = 0
                    totSpareCap = ebc - disFormula

                disAmountTax = disAmount * (corporate_tax / 100)
                totSpareCapTax = totSpareCap * (corporate_tax / 100)
                intSpareCap = 0
                intSpareCapTax = intSpareCap * (corporate_tax / 100)

                # Construct Table
                workings = html.Div([
                    dbc.Row([
                        dbc.Col([html.Div('')], width=5),
                        dbc.Col([html.Div(html.B('Amount')), ], width=3),
                        dbc.Col([html.Div(html.B('Tax Value'))], width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div('Disallowed Amount: '),
                            html.Div('Total Spare Capacity: '),
                        ], width=5),
                        dbc.Col([
                            html.Div('€{:,.2f}'.format(disAmount)),
                            html.Div('€{:,.2f}'.format(totSpareCap)),
                        ], width=3),
                        dbc.Col([
                            html.Div('€{:,.2f}'.format(disAmountTax)),
                            html.Div('€{:,.2f}'.format(totSpareCapTax)),
                        ], width=3)
                    ])

                ])

                ### Disallowance Formula not applied
            #### Interest Spare Capacity calculated here
            else:
                intSpareCap = -ebc + intcalc
                intSpareCapTax = intSpareCap * (corporate_tax / 100)

                # retune other calculations
                disFormula = "Not Assigned"
                disAmount = 0
                totSpareCap = 0
                disAmountTax = disAmount * (corporate_tax / 100)
                totSpareCapTax = totSpareCap * (corporate_tax / 100)

                workings = html.Div([
                    dbc.Row([
                        dbc.Col([html.Div('')], width=5),
                        dbc.Col([html.Div('Amount')], width=3),
                        dbc.Col([html.Div('Tax Value')], width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div('Interest Spare Capacity: '),
                        ], width=5),
                        dbc.Col([
                            html.Div('€{:,.2f}'.format(intSpareCap)),
                        ], width=3),
                        dbc.Col([
                            html.Div('€{:,.2f}'.format(intSpareCapTax)),

                        ], width=3)
                    ])

                ])
    return workings


##-------DISALLOWANCE WORKING CALLBACK----------------------
@dash_app.callback(
    Output('dis-workings-output', 'children'),
    Input('ebc_store', 'data'),
    Input('group_ratio_store', 'data'),
    Input('tax_ebitda_store', 'data'),
    Input('ebc_store_spareCap', 'data'),
    Input('ebc_store_intcalc', 'data'),
    Input('equity_ratio_store_group', 'data'),
    Input('equity_ratio_store_worldwide', 'data'),
    Input('tax_ebitda_store_lim_spare_cap', 'data')
)
def disallowance_workings(ebcPre, groupRatPre, ebitdaPre, iscPre, intcalcPre, erGroupPre, erWrldPre, lscPre):
    # if n_clicks > 0:
    # Call our formatting functions
    ebc = euroformatting(ebcPre, "ebc", 0)
    groupRat = formatting(groupRatPre, "group_ratio", 0)
    ebitda = euroformatting(ebitdaPre, "tax_ebitda", 0)
    isc = formatting(iscPre, "spare_capacity", 0)
    intcalc = formatting(intcalcPre, "intcalc", 0)

    erGroup = formatting(erGroupPre, "group", 0)
    erWrld = formatting(erWrldPre, "worldwide", 0)
    lsc = formatting(lscPre, "limit_spare_capacity", 0)
    # "Fails interest restrictions. Disallowance applied."
    if erGroup == 0 and erWrld == 0:

        # getting errors with this
        equityRatioResponse = "No workings to show - Equity Ratio Test not completed yet"

        workings = html.Div(
            [html.Div(html.B("Step 1: Equity Ratio Test")),
             equityRatioResponse,

             ])


    else:
        value = round(float(erWrld) - float(erGroup), 10)
        if value <= .02:
            equityRatioResponse = html.Div(
                [
                    dbc.Row([
                        dbc.Col([
                            html.Div('Equity Ratio Worldwide:', style={'font-size': '80%'}),
                            html.Div('LESS Equity Ratio Group:', style={'font-size': '80%'}),
                            html.Div('=', style={'font-size': '80%'}),
                            html.Div('%', style={'font-size': '80%'})
                        ], width=6),

                        dbc.Col([
                            html.Div('{:.2f}%'.format(100 * erWrld), style={'text-align': 'right', 'font-size': '80%'}),
                            html.Div(html.U('{:.2f}%'.format(100 * erGroup)),
                                     style={'text-align': 'right', 'font-size': '80%'}),
                            html.Div(html.B('{:,.2f}'.format(value)),
                                     style={'text-align': 'right', 'font-size': '80%'}),
                            html.Div(html.B('{:,.2f}%'.format(100 * value)),
                                     style={'text-align': 'right', 'font-size': '80%'})
                        ], width=2)
                    ]),
                    html.Div("As {:,.2f}% ≤ 2%: No disallowance applied".format(100 * value),
                             style={'font-size': '80%'})
                ])
            workings = html.Div(
                [html.Div(html.B("Step 1: Equity Ratio Test", style={'font-size': '80%'})),
                 equityRatioResponse,
                 ])
        else:
            equityRatioResponse = html.Div(
                [
                    dbc.Row([
                        dbc.Col([
                            html.Div('Equity Ratio Worldwide', style={'font-size': '80%'}),
                            html.Div('LESS Equity Ratio Group:', style={'font-size': '80%'}),
                            html.Div('=', style={'font-size': '80%'}),
                            html.Div('%', style={'font-size': '80%'})
                        ], width=6),

                        dbc.Col([
                            html.Div('{:.2f}%'.format(100 * erWrld), style={'text-align': 'right', 'font-size': '80%'}),
                            html.Div(html.U('{:.2f}%'.format(100 * erGroup)),
                                     style={'text-align': 'right', 'font-size': '80%'}),
                            html.Div(html.B('{:.2f}'.format(value)), style={'text-align': 'right', 'font-size': '80%'}),
                            html.Div(html.B('{:.2f}%'.format(100 * value)),
                                     style={'text-align': 'right', 'font-size': '80%'})
                        ], width=2)
                    ]),
                    html.Div("As {:.2f}% > 2%: Disallowance applied".format(100 * value), style={'font-size': '80%'})
                ])

            ### If EBC Positive, apply disallowance formula
            #### Disallowance and TotSpareCap returned (along with respective tax values)
            if ebc > 0:

                ebcResponse = html.Div(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.Div('Exceeding Borrowing Costs:', style={'font-size': '80%'})
                            ], width=6),

                            dbc.Col([
                                html.Div('€{:,.2f}'.format(ebc), style={'text-align': 'right', 'font-size': '80%'})
                            ], width=2)
                        ]),
                        html.Div("As €{:,.2f} > 0: Disallowance applied".format(ebc), style={'font-size': '80%'})
                    ])
                # Check if group ratio or 30% is greater
                if groupRat > 0.3:
                    disFormula = (groupRat * ebitda) + lsc + isc
                    groupRatFormula = html.Div(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.Div('As Group Ratio ({}%) > 30%:'.format(100 * groupRat),
                                             style={'font-size': '80%'}),
                                    html.Div('Group Ratio:', style={'font-size': '80%'}),
                                    html.Div('MULTIPLY BY Tax EBITDA:', style={'font-size': '80%'}),
                                    html.Div('ADD Limited Spare Capacity:', style={'font-size': '80%'}),
                                    html.Div('ADD Interest Spare Capacity:', style={'font-size': '80%'}),
                                    html.Div('Total:', style={'font-size': '80%'}),
                                ], width=6),

                                dbc.Col([
                                    html.P(""),
                                    html.Div('{:.2f}%'.format(100 * groupRat),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div('€{:,.2f}'.format(ebitda),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div('€{:,.2f}'.format(lsc), style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.U('€{:,.2f}'.format(isc)),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div('€{:,.2f}'.format(disFormula),
                                             style={'text-align': 'right', 'font-size': '80%'})
                                ], width=2)
                            ]),
                        ])
                else:
                    disFormula = (0.3 * ebitda) + lsc + isc
                    groupRatFormula = html.Div(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.Div('As 30% > Group Ratio ({}%):'.format(100 * groupRat),
                                             style={'font-size': '80%'}),
                                    html.Div(""),
                                    html.Div('MULTIPLY BY Tax EBITDA:', style={'font-size': '80%'}),
                                    html.Div('ADD Limited Spare Capacity:', style={'font-size': '80%'}),
                                    html.Div('ADD Interest Spare Capacity:', style={'font-size': '80%'}),
                                    html.Div('Total:'),
                                ], width=6),

                                dbc.Col([
                                    html.Div(""),
                                    html.Div('30%', style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div('€{:,.2f}'.format(ebitda),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div('€{:,.2f}'.format(lsc), style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.U('€{:,.2f}'.format(isc)),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div('€{:,.2f}'.format(disFormula),
                                             style={'text-align': 'right', 'font-size': '80%'})
                                ], width=2)
                            ]),
                        ])

                # Compare disallowance formula to EBC
                # Total Spare Capacity calculated here
                if disFormula < ebc:
                    disAmount = ebc - disFormula
                    totSpareCap = 0
                    disallowed_amount = html.Div(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(
                                        'As Exceeding Borrowing Costs (€{:,.2f}) > €{:,.2f} :'.format(ebc, disFormula),
                                        style={'font-size': '80%'}),
                                    html.Div(html.U("Disallowed Amount:"), style={'font-size': '80%'}),
                                    html.Div('Exceeding Borrowing Costs:', style={'font-size': '80%'}),
                                    html.Div('LESS :', style={'font-size': '80%'}),
                                    html.Div('Total:', style={'font-size': '80%'}),
                                    html.Div('@ 12.5%:', style={'font-size': '80%'}),

                                    html.Br(),
                                    html.Div(html.U('Total Spare Capacity:', style={'font-size': '80%'})),
                                    html.Div('Total:', style={'font-size': '80%'}),
                                    html.Div('@ 12.5%:', style={'font-size': '80%'}),

                                ], width=6),

                                dbc.Col([
                                    html.Br(),
                                    html.Br(),
                                    html.Div('€{:,.2f}'.format(ebc), style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.U('€{:,.2f}'.format(disFormula)),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.B('€{:,.2f}'.format(disAmount)),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.B('€{:,.2f}'.format(disAmount * .125)),
                                             style={'text-align': 'right', 'font-size': '80%'}),

                                    html.Br(),
                                    html.Br(),
                                    html.Div(html.B('€0.00'), style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.B('€0.00'), style={'text-align': 'right', 'font-size': '80%'})
                                ], width=2)
                            ]),
                        ])


                else:
                    disAmount = 0
                    totSpareCap = ebc - disFormula

                    disallowed_amount = html.Div(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(
                                        'As Exceeding Borrowing Costs (€{:,.2f}) <= €{:,.2f} :'.format(ebc, disFormula),
                                        style={'font-size': '80%'}),
                                    html.Div(html.U("Disallowed Amount:", style={'font-size': '80%'})),
                                    html.Div('Total:', style={'font-size': '80%'}),
                                    html.Div('@ 12.5%: ', style={'font-size': '80%'}),

                                    html.Br(),
                                    html.Div(html.U('Total Spare Capacity:', style={'font-size': '80%'})),
                                    html.Div('Exceeding Borrowing Costs:', style={'font-size': '80%'}),
                                    html.Div('LESS :', style={'font-size': '80%'}),
                                    html.Div('Total:', style={'font-size': '80%'}),
                                    html.Div('@ 12.5%:', style={'font-size': '80%'})

                                ], width=6),

                                dbc.Col([
                                    html.Br(),
                                    html.Br(),
                                    html.Div(html.B('€0.00'), style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.B('€0.00'), style={'text-align': 'right', 'font-size': '80%'}),

                                    html.Br(),
                                    html.Br(),
                                    html.Div('€{:,.2f}'.format(ebc), style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.U('€{:,.2f}'.format(disFormula)),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.B('€{:,.2f}'.format(disAmount)),
                                             style={'text-align': 'right', 'font-size': '80%'}),
                                    html.Div(html.B('€{:,.2f}'.format(disAmount * .125)),
                                             style={'text-align': 'right', 'font-size': '80%'})
                                ], width=2)
                            ]),
                        ])

                disAmountTax = disAmount * (corporate_tax / 100)
                totSpareCapTax = totSpareCap * (corporate_tax / 100)
                intSpareCap = 0
                intSpareCapTax = intSpareCap * (corporate_tax / 100)

                workings = html.Div(
                    [html.Div(html.B("Step 1: Equity Ratio Test")),
                     equityRatioResponse,
                     html.P(""),
                     html.Div(html.B("Step 2: Exceeding Borrowing Costs Test")),
                     ebcResponse,
                     html.P(""),
                     html.Div(html.B("Step 3: Group Ratio Check")),
                     groupRatFormula,
                     html.P(""),
                     html.Div(html.B("Step 4: Disallowed Amount")),
                     disallowed_amount
                     ])


            ### Disallowance Formula not applied
            #### Interest Spare Capacity calculated here
            else:

                ebcResponse = html.Div(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.Div('Exceeding Borrowing Costs:', style={'font-size': '80%'})
                            ], width=6),

                            dbc.Col([
                                html.Div('€{:,.2f}'.format(ebc), style={'text-align': 'right', 'font-size': '80%'})
                            ], width=2)
                        ]),
                        html.Div("As €{:,.2f} < 0: Disallowance not applied.".format(ebc), style={'font-size': '80%'})
                    ])

                groupRatFormula = html.Div("N/A")

                intSpareCap = -ebc + intcalc
                intSpareCapTax = intSpareCap * (corporate_tax / 100)

                # retune other calculations
                disFormula = "Not Assigned"
                disAmount = 0
                totSpareCap = 0
                disAmountTax = disAmount * (corporate_tax / 100)
                totSpareCapTax = totSpareCap * (corporate_tax / 100)

                disallowed_amount = html.Div(
                    [
                        dbc.Row([
                            dbc.Col([
                                # html.Div(html.U('Amount:')),
                                html.Div("Interest Spare Capacity:", style={'font-size': '80%'}),
                                html.Div("LESS Exceeding Borrowing Costs:", style={'font-size': '80%'}),
                                html.Div('Total:', style={'font-size': '80%'}),
                                html.Div('@ 12.5%:', style={'font-size': '80%'}),

                            ], width=6),

                            dbc.Col([
                                # html.Br(),
                                html.Div('€{:,.2f}'.format(intcalc), style={'text-align': 'right', 'font-size': '80%'}),
                                html.Div(html.U('€{:,.2f}'.format(ebc)),
                                         style={'text-align': 'right', 'font-size': '80%'}),
                                html.Div(html.B('€{:,.2f}'.format(intSpareCap)),
                                         style={'text-align': 'right', 'font-size': '80%'}),
                                html.Div(html.B('€{:,.2f}'.format(intSpareCapTax)),
                                         style={'text-align': 'right', 'font-size': '80%'}),

                            ], width=2)
                        ]),
                    ])

                workings = html.Div(
                    [html.Div(html.B("Step 1: Equity Ratio Test")),
                     equityRatioResponse,
                     html.P(""),
                     html.Div(html.B("Step 2: Exceeding Borrowing Costs Test")),
                     ebcResponse,
                     html.P(""),
                     html.Div(html.B("Step 3: Amount")),
                     disallowed_amount
                     ])

    return workings


##-------IMPORTING STORED VALUES CALLBACKS-------------------

@dash_app.callback(
    Output("equityRatioGrpCalc", "children"),
    Input("equity_ratio_store_group", "data")
)
def disallowanceImport(data):
    if data == [{}]:
        return "No Equity Ratio Group Calculation retrieved yet"
    else:
        ergc = data[0]
        try:
            float(ergc["group"])
            return "Group Calculation: {:.2f}%".format(100 * float(ergc["group"]))
        except ValueError:
            return "No Equity Ratio Group calculation saved yet"


@dash_app.callback(
    Output("equityRatioWrldCalc", "children"),
    Input("equity_ratio_store_worldwide", "data")
)
def disallowanceImport(data):
    if data == [{}]:
        return "No Equity Ratio Worldwide calculation retrieved yet"
    else:
        erwc = data[0]
        try:
            float(erwc["worldwide"])
            return "Worldwide Calculation: {:.2f}%".format(100 * float(erwc["worldwide"]))
        except ValueError:
            return "No Equity Ratio Worldwide calculation saved yet"


@dash_app.callback(
    Output("deMinimis", "children"),
    Input("ebc_store_dm", "data")
)
def disallowanceImport(data):
    if data == [{}]:
        return "No Exceeding Borrowing Costs De Minimis calculation retrieved yet"
    else:
        ebc_dm = data[0]
        return "Exceeding Borrowing Costs De Minimis: {}".format(ebc_dm["ebc_dm"])


@dash_app.callback(
    Output("ebctest", "children"),
    Input("ebc_store", "data")
)
def disallowanceImport(data):
    if data == [{}]:
        return "No Exceeding Borrowing Costs calculation retrieved yet"
    else:
        ebc = data[0]
        return "Exceeding Borrowing Costs: {}".format(ebc["ebc"])


##-------DISALLOWANCE STORE CALLBACK---------------
@dash_app.callback(
    Output('disallowance_store', 'data'),
    # Input('dis-calculate', 'n_clicks'),
    # State('within-output', 'children'),
    # State('sign-output', 'children'),
    Input('ebc_store', 'data'),
    Input('group_ratio_store', 'data'),
    Input('tax_ebitda_store', 'data'),
    Input('ebc_store_spareCap', 'data'),
    Input('ebc_store_intcalc', 'data'),
    Input('equity_ratio_store_group', 'data'),
    Input('equity_ratio_store_worldwide', 'data'),
    Input('tax_ebitda_store_lim_spare_cap', 'data')
)
### Limited Spare Capacity needed
def return_disallowance(ebcPre, groupRatPre, ebitdaPre, iscPre, intcalcPre, erGroupPre, erWrldPre, lscPre):
    # if n_clicks > 0:
    # Call our formatting functions
    if ebcPre != [{}] and groupRatPre != [{}] and ebitdaPre != [{}] and iscPre != [{}] and intcalcPre != [
        {}] and erGroupPre != [{}] and erWrldPre != [{}] and lscPre != [{}]:
        ebc = euroformatting(ebcPre, "ebc", 0)
        groupRat = formatting(groupRatPre, "group_ratio", 0)
        ebitda = euroformatting(ebitdaPre, "tax_ebitda", 0)
        isc = formatting(iscPre, "spare_capacity", 0)
        intcalc = formatting(intcalcPre, "intcalc", 0)
        erGroup = formatting(erGroupPre, "group", 0)
        erWrld = formatting(erWrldPre, "worldwide", 0)
        lsc = formatting(lscPre, "limit_spare_capacity", 0)

        # "Fails interest restrictions. Disallowance applied."
        if erGroup == 0 and erWrld == 0:
            data = html.H6("Equity Ratio Test not completed yet")
        elif erGroup == 0 or erWrld == 0:
            data = html.H6("Equity Ratio Test not fully completed yet")
        else:
            value = round(float(erGroup) / float(erWrld), 10)
            if value <= .02:
                data = "Passes Interest restrictions: No disallowance applied"
            else:
                ### If EBC Positive, apply disallowance formula
                #### Disallowance and TotSpareCap returned (along with respective tax values)
                if ebc > 0:
                    # Check if group ratio or 30% is greater
                    if groupRat > 0.3:
                        disFormula = (groupRat * ebitda) + lsc + isc
                    else:
                        disFormula = (0.3 * ebitda) + lsc + isc

                    # Compare disallowance formula to EBC
                    # Total Spare Capacity calculated here
                    if disFormula < ebc:
                        disAmount = ebc - disFormula
                        totSpareCap = 0

                    else:
                        disAmount = 0
                        totSpareCap = ebc - disFormula

                    disAmountTax = disAmount * (corporate_tax / 100)
                    totSpareCapTax = totSpareCap * (corporate_tax / 100)
                    intSpareCap = 0
                    intSpareCapTax = intSpareCap * (corporate_tax / 100)

                    data = [{'disAmount': disAmount, 'disAmountTax': disAmountTax, 'totSpareCap': totSpareCap,
                             'totSpareCapTax': totSpareCapTax, 'intSpareCap': intSpareCap,
                             'intSpareCapTax': intSpareCapTax}]


                ### Disallowance Formula not applied
                #### Interest Spare Capacity calculated here
                else:
                    intSpareCap = -ebc + intcalc
                    intSpareCapTax = intSpareCap * (corporate_tax / 100)

                    # retune other calculations
                    disFormula = "Not Assigned"
                    disAmount = 0
                    totSpareCap = 0
                    disAmountTax = disAmount * (corporate_tax / 100)
                    totSpareCapTax = totSpareCap * (corporate_tax / 100)

                    data = [{'intSpareCap': intSpareCap, 'intSpareCapTax': intSpareCapTax}]

        return data


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##-------------------------------SUMMARY PAGE-------------------------------
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##-------------------------------SUMMARY VARIABLES--------------------------

##-------------------------------SUMMARY LAYOUT--------------------------


summary_card = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        
                        html.Div(html.H2("Summary", className="card-title", style={'color': kpmgBlue_hash}), style={'display': 'inline-block'}),
                        
                        html.Div(html.I(id="popover-target7", className="bi bi-info-circle-fill me-2", style={'display': 'inline-block'}), style={'margin-left':'10px', 'display': 'inline-block'})
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

summary_layout = summary_card


##-------------------------------SUMMARY CALLBACKS--------------------------


##-------GET EBC VALUE FROM STORE CALLBACK-----------
@dash_app.callback(Output(component_id='summary-borrowing-calc-output', component_property='children'),
                   Input('ebc_store', 'data'),
                   )
def borrowing_costs(ebc):
    if ebc == [{}]:
        output = dbc.Row([
            dbc.Col([html.Div("Exceeding Borrowing Costs:")], width=6),
            dbc.Col([html.Div("Not yet calculated")], width=5)
        ])
        return output
    else:
        ebc_dict = ebc[0]
        output = dbc.Row([
            dbc.Col([html.Div("Exceeding Borrowing Costs:")], width=6),
            dbc.Col([html.Div("{}".format(ebc_dict["ebc"]))], width=5)
        ])
        return output


##------GET EBC DM VALUE FROM STORE CALLBACK----------
@dash_app.callback(Output(component_id='summary-borrowing-calc-output-dm', component_property='children'),
                   Input('ebc_store_dm', 'data')
                   )
def borrowing_costs(ebc_dm):
    if ebc_dm == [{}]:
        output = dbc.Row([
            dbc.Col([html.Div("Exceeding Borrowing Costs for the De Minimis Exemption:")], width=6),
            dbc.Col([html.Div("Not yet calculated")], width=5)
        ])
        return output
    else:
        ebc_dm_dict = ebc_dm[0]
        output = dbc.Row([
            dbc.Col([html.Div("Exceeding Borrowing Costs for the De Minimis Exemption:")], width=6),
            dbc.Col([html.Div("{}".format(ebc_dm_dict["ebc_dm"]))], width=5)
        ])
        return output


##-------GET TAX EBITDA VALUE FROM STORE CALLBACK-----------
@dash_app.callback(Output(component_id='summary-tax-ebitda-output', component_property='children'),
                   Input('tax_ebitda_store', 'data'))
def tax_ebitda_(tax_ebitda):
    if tax_ebitda == [{}]:
        output = dbc.Row([
            dbc.Col([html.Div("Tax EBITDA:")], width=6),
            dbc.Col([html.Div("Not yet calculated")], width=5)
        ])
        return output
    else:
        tax_ebitda_dict = tax_ebitda[0]
        output = dbc.Row([
            dbc.Col([html.Div("Tax EBITDA:")], width=6),
            dbc.Col([html.Div("{}".format(tax_ebitda_dict['tax_ebitda']))], width=5)
        ])
        return output


##-------GET GROUP RATIO VALUE FROM STORE CALLBACK-----------
@dash_app.callback(Output(component_id='summary-group-ratio-output', component_property='children'),
                   Input('group_ratio_store', 'data'))
def group_ratio(group_ratio):
    if group_ratio == [{}]:
        output = dbc.Row([
            dbc.Col([html.Div("Group Ratio:")], width=6),
            dbc.Col([html.Div("Not yet calculated")], width=5)
        ])
        return output
    else:
        group_ratio_dict = group_ratio[0]
        try:
            float(group_ratio_dict['group_ratio'])
            output = dbc.Row([
                dbc.Col([html.Div("Group Ratio:")], width=6),
                dbc.Col([html.Div("{:.2f}%".format(100 * float(group_ratio_dict['group_ratio'])))], width=5)
            ])
        except ValueError:
            output = dbc.Row([
                dbc.Col([html.Div("Group Ratio:")], width=6),
                dbc.Col([html.Div("{}".format(group_ratio_dict['group_ratio']))], width=5)
            ])
        return output


##-------GET EQUITY RATIO GROUP VALUE FROM STORE CALLBACK-----------
@dash_app.callback(Output(component_id='summary-equity-ratio-output-group', component_property='children'),
                   Input('equity_ratio_store_group', 'data'))
def equity_ratio(equity_ratio):
    if equity_ratio == [{}]:
        output = dbc.Row([
            dbc.Col([html.Div("Interest Group Calculation:")], width=6),
            dbc.Col([html.Div("Not yet calculated")], width=5)
        ])
        return output
    else:
        equity_ratio_dict_group = equity_ratio[0]
        try:
            float(equity_ratio_dict_group['group'])
            group_value = float(equity_ratio_dict_group['group'])
            output = dbc.Row([
                dbc.Col([html.Div("Interest Group Calculation:")], width=6),
                dbc.Col([html.Div("{:.2f}%".format(100 * group_value))], width=5)
            ])
        except ValueError:
            group_value = equity_ratio_dict_group['group']
            output = dbc.Row([
                dbc.Col([html.Div("Interest Group Calculation:")], width=6),
                dbc.Col([html.Div("{}".format(group_value))], width=5)
            ])
        return output


##-------GET EQUITY RATIO WORLDWIDE VALUE FROM STORE CALLBACK-----------
@dash_app.callback(Output(component_id='summary-equity-ratio-output-worldwide', component_property='children'),
                   Input('equity_ratio_store_worldwide', 'data'))
def equity_ratio(equity_ratio):
    if equity_ratio == [{}]:
        output = dbc.Row([
            dbc.Col([html.Div("Worldwide Group Calculation:")], width=6),
            dbc.Col([html.Div("Not yet calculated")], width=5)
        ])
        return output
    else:
        equity_ratio_dict_worldwide = equity_ratio[0]
        try:
            float(equity_ratio_dict_worldwide['worldwide'])
            worldwide_value = float(equity_ratio_dict_worldwide['worldwide'])
            output = dbc.Row([
                dbc.Col([html.Div("Worldwide Group Calculation:")], width=6),
                dbc.Col([html.Div("{:.2f}%".format(100 * worldwide_value))], width=5)
            ])
        except ValueError:
            worldwide_value = equity_ratio_dict_worldwide['worldwide']
            output = dbc.Row([
                dbc.Col([html.Div("Worldwide Group Calculation:")], width=6),
                dbc.Col([html.Div("{}".format(worldwide_value))], width=5)
            ])
        return output


##-------GET DISALLOWANCE FORMULA VALUE FROM STORE CALLBACK-----------
@dash_app.callback(Output(component_id='summary-disallowance-output', component_property='children'),
                   Input('disallowance_store', 'data'),
                   )
def disallowance(disallowance):
    if disallowance == [{}]:
        output = dbc.Row([
            dbc.Col([html.Div("Not yet calculated")], width=6)
        ])
        return output
    else:
        if isinstance(disallowance, str):
            output = disallowance
            return output
        else:
            disallowanceDict = disallowance[0]
            if len(disallowanceDict) == 2:
                output = html.Div([
                    dbc.Row([
                        dbc.Col([html.Div('')], width=6),
                        dbc.Col([html.Div(html.B('Amount'))], width=3),
                        dbc.Col([html.Div(html.B('Tax Value'))], width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div('Interest Spare Capacity: '),
                        ], width=6),
                        dbc.Col([
                            html.Div('€{:,.2f}'.format(disallowanceDict["intSpareCap"])),
                        ], width=3),
                        dbc.Col([
                            html.Div('€{:,.2f}'.format(disallowanceDict["intSpareCapTax"])),

                        ], width=3)
                    ])

                ])
            elif len(disallowanceDict) == 6:
                output = html.Div([
                    dbc.Row([
                        dbc.Col([html.Div("")], width=6),
                        dbc.Col([html.Div(html.B("Amount"))], width=3),
                        dbc.Col([html.Div(html.B("Tax Value"))], width=3),

                    ]),
                    dbc.Row([
                        dbc.Col([html.Div("Disallowance Applied:")], width=6),
                        dbc.Col([html.Div("€{:,.2f}".format(disallowanceDict["disAmount"]))], width=3),
                        dbc.Col([html.Div("€{:,.2f}".format(disallowanceDict["disAmountTax"]))], width=3),
                    ]),
                    dbc.Row([
                        dbc.Col([html.Div("Total Spare Capacity:")], width=6),
                        dbc.Col([html.Div("€{:,.2f}".format(disallowanceDict["totSpareCap"]))], width=3),
                        dbc.Col([html.Div("€{:,.2f}".format(disallowanceDict["totSpareCapTax"]))], width=3),
                    ]),
                    dbc.Row([
                        dbc.Col([html.Div("Interest Spare Capacity:")], width=6),
                        dbc.Col([html.Div("€{:,.2f}".format(disallowanceDict["intSpareCap"]))], width=3),
                        dbc.Col([html.Div("€{:,.2f}".format(disallowanceDict["intSpareCapTax"]))], width=3),
                    ])
                ])
        return output


###-------------PAGE NAVIGATION-----------------------------------------------------------
@dash_app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('login_store', 'data')
)
def display_page(pathname, login):
    ## authentication test
    if login == [{'uname': 'tax', 'passw': 'tax123'}]:
        authentication = 'Y'
    else:
        authentication = 'N'

    ## path mapping

    if authentication == 'Y':
        if pathname == '/':
            return home_layout
        if pathname == '/home':
            return home_layout
        elif pathname == '/exceeding-borrowing-costs':
            return ebc_layout
        elif pathname == '/tax-ebitda':
            return ebitda_layout
        elif pathname == '/group-ratio':
            return gr_layout
        elif pathname == '/equity-ratio':
            return er_layout
        elif pathname == '/disallowance-formula':
            return disallowance_layout
        elif pathname == '/summary':
            return summary_layout
        else:
            return '404'

    if authentication == 'N':
        if pathname == '/home':
            return index_page
        elif pathname == '/exceeding-borrowing-costs':
            return index_page
        elif pathname == '/tax-ebitda':
            return index_page
        elif pathname == '/group-ratio':
            return index_page
        elif pathname == '/equity-ratio':
            return index_page
        elif pathname == '/disallowance-formula':
            return index_page
        elif pathname == '/summary':
            return index_page
        else:
            return index_page


if __name__ == '__main__':
    dash_app.run_server(debug=True)