import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    html.H1("Web QA Tools Powered by Dash and Pylinac"),

    html.Div(children='''
        Drag, Drop, Download.
    '''),

])