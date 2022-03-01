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


#########################################################################
##--------------EBC Callbacks------------------------------------------

##-------------------------------EBC CALLBACKS--------------------------------

group_dummy = ["N/A"]
company_dummy = ["N/A"]
interest_group_dummy = ["Interest Expense", "Interest Income", "Interest Spare Capacity"]
tax_rates = [12.5, 25, 33]
currencies = ['Euro (€)', 'USD ($)']
column_names = ['Group', 'Company', 'Interest Type', 'Amount (€)', 'Tax Rate (%)', 'Legacy Debt',
                'PBI Amount (€)', 'Text Description']
ebc_df = pd.DataFrame(columns=column_names)

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