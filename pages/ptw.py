import base64
import io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, callback
from dash import html
import plotly.express as px
import pandas as pd

from ptw_ext import parse_qa_data_io, ptw_plotting_limits

dash.register_page(__name__)

names = ["CAX", "G10", "L10", "T10", "R10", "G20", "L20", "T20", "R20", "E1", "E2", "E3", "E4", "CAX_normed", "Flatness", "SymmetryGT", "SymmetryLR", "BQF"]

layout = html.Div(children=[
    html.H1(children="PTW QUICKCHECK"),

    dcc.Upload(
        id="ptw-upload-data",
        children=html.Div([
            "Drag and Drop or ",
            html.A("Select Files")
        ]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px"
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),

    html.Div([html.Div("Worklist: "), 
              dcc.Dropdown(id="ptw-worklist-selector"),
              html.Div("Treatment Unit: "), 
              dcc.Dropdown(id="ptw-treatment-unit-selector"),
        ]),

    dcc.Checklist(
        id="ptw-column_name_selector",
        options=[{"label": c, "value": c} for c in names]
    ),

    dcc.Graph(
        id="ptw-output-figure"
    ),

    dcc.Store(id="ptw-cache-data")
])


def parse_contents(contents):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    return parse_qa_data_io(io.StringIO(decoded.decode("utf-8")))


@callback(Output("ptw-cache-data", "data"),
          Input("ptw-upload-data", "contents"),
          State("ptw-upload-data", "filename"),
          State("ptw-upload-data", "last_modified"), prevent_initial_call=True)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        dataframes = []
        for contents in list_of_contents:
            dataframes.append(parse_contents(contents))
        df = pd.concat(dataframes)
        df.sort_values("Date", inplace=True)


        return df.to_json(date_format="iso", orient="split")


    return None, None


@callback(Output("ptw-worklist-selector", "options"),
          Output("ptw-worklist-selector", "value"),
          Input("ptw-cache-data", "data"), prevent_initial_call=True)
def create_worklist_selector(data):
    if data is not None:
        df = pd.read_json(data, orient="split")
        worklists = df["Worklist"].unique()
        worklists.sort()
        worklist_options=[
            {"label": w, "value": w} for w in worklists
        ]

        return worklist_options, worklists[0]

    return None, None


@callback(Output("ptw-treatment-unit-selector", "options"),
          Output("ptw-treatment-unit-selector", "value"),
          Input("ptw-cache-data", "data"),
          Input("ptw-worklist-selector", "value"), 
          prevent_initial_call=True)
def create_treatment_unit_selector(data, worklist):
    if data is not None and worklist is not None:
        df = pd.read_json(data, orient="split")

        df = df[df["Worklist"] == worklist]

        treatment_units = df["TreatmentUnit"].unique()
        treatment_units.sort()
        treatment_options=[
            {"label": w, "value": w} for w in treatment_units
        ]

        return treatment_options, treatment_units[0]

    return None, None



@callback(Output("ptw-output-figure", "figure"),
          Input("ptw-cache-data", "data"),
          Input("ptw-worklist-selector", "value"),
          Input("ptw-treatment-unit-selector", "value"), 
          Input("ptw-column_name_selector", "value"),
          prevent_initial_call=True)
def update_figure(data, worklist, treatment_unit, columns):
    if columns is not None and len(columns) > 0:

        df = pd.read_json(data, orient="split")
        df = df[(df["Worklist"] == worklist) & (df["TreatmentUnit"] == treatment_unit)]
        fig = px.line(df, x="Date", y=columns)

        if len(columns) == 1 and columns[0] in ptw_plotting_limits:
            fig.update_yaxes(range=ptw_plotting_limits[columns[0]][:-1])

        return fig
    return {}
