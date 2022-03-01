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

import home ##, ebc, group_ratio, Tax_EBITDA, equity_ratio, summary, disallowance
import ebc

corporate_tax = 12.5
kpmgBlue_hash = '#00338D'
dash_app = dash.Dash(__name__, suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])
app = dash_app.server

home_df = pd.DataFrame(columns=['Group', 'Company', 'In Interest Group?'])
currencies = ['Euro (€)', 'USD ($)', 'GBP (£)', 'Other']

##-------------------------------PAGE COMPONENTS--------------------------------------------------

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

##-----------------------------CALLBACKS---------------------------------------------------------

##--------------------------HOME CALLBACKS--------------------------------------------------------
#################################################################################################


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

# callback - defines which page each URL sends the user to
@dash_app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return home.layout
    # elif pathname == '/summary':
    #     return summary.layout
    elif pathname == '/exceeding-borrowing-costs':
        return ebc.layout
    # elif pathname == '/tax-ebitda':
    #     return Tax_EBITDA.layout
    # elif pathname == '/group-ratio':
    #     return group_ratio.layout
    # elif pathname == '/equity-ratio':
    #     return equity_ratio.layout
    # elif pathname == '/disallowance-formula':
    #     return disallowance.layout
    else:
        return '404'


# to run the code
if __name__ == '__main__':
    dash_app.run_server(debug=True)