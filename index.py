import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

#from app import app
from apps import home ##, ebc, group_ratio, Tax_EBITDA, equity_ratio, summary, disallowance

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.ZEPHYR])


kpmgBlue_hash = '#00338D'

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
            )

        ]),

        # navigation links to different pages
        dbc.Row(
            [
                # title and subtitle
                html.Div(html.H2("ILR Tax Model", style={"color": "#FFFFFF"}), style={'text-align': 'center'}),
                html.Hr(),
                # setting up page contents
                dbc.Nav(
                    [
                        dbc.NavLink("Initial Setup", href="/", style={"color": "#D3D3D3"}, active="exact"),
                        dbc.NavLink("Exceeding Borrowing Costs", href="/exceeding-borrowing-costs",
                                    style={"color": "#D3D3D3"}, active="exact"),
                        dbc.NavLink("Tax EBITDA", href="/tax-ebitda", style={"color": "#D3D3D3"}, active="exact"),
                        dbc.NavLink("Group Ratio", href="/group-ratio", style={"color": "#D3D3D3"}, active="exact"),
                        dbc.NavLink("Equity Ratio", href="/equity-ratio", style={"color": "#D3D3D3"}, active="exact"),
                        dbc.NavLink("Disallowance Formula", href="/disallowance-formula", style={"color": "#D3D3D3"},
                                    active="exact"),
                        dbc.NavLink("Summary", href="/summary", style={"color": "#D3D3D3"}, active="exact")

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

##---------------------------LAYOUT------------------------------------------------------------

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    content,

    ##---MEMORY STORES---

    # Store component for tabs
    dcc.Store(id='home_store', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store_dm', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store_intcalc', data=[{}], storage_type="session"),
    dcc.Store(id='ebc_store_spareCap', data=[{}], storage_type="session"),
    dcc.Store(id='tax_ebitda_store', data=[{}], storage_type="session"),
    dcc.Store(id='tax_ebitda_store_lim_spare_cap', data=[{}], storage_type="session"),
    dcc.Store(id='group_ratio_store', data=[{}], storage_type="session"),
    dcc.Store(id='equity_ratio_store_group', data=[{}], storage_type="session"),
    dcc.Store(id='equity_ratio_store_worldwide', data=[{}], storage_type="session")
])


##-----------------------------CALLBACKS---------------------------------------------------------

# callback - defines which page each URL sends the user to
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return home.layout
    # elif pathname == '/summary':
    #     return summary.layout
    # elif pathname == '/exceeding-borrowing-costs':
    #     return ebc.layout
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
    app.run_server(debug=True)
