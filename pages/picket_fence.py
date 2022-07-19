from pylinac.picketfence import PicketFence, MLC

import dash

from dash import Dash, html, dcc, dash_table, callback
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

from pylinac_ext.picket_fence import plot_analyzed_image
from dash_ext.matplotlib import fig_to_uri

import io
import base64
from pathlib import Path

dash.register_page(__name__)

class Analysis(object):
    def __init__(self):
        self.pf = None
        self.input_file = None

    def analyze(self, dcm_file, filename=None):
        self.input_file = filename
        self.pf = PicketFence(dcm_file, mlc=MLC.MILLENNIUM)
        self.pf.analyze(tolerance=1.0, action_tolerance=0.3)

    def get_results(self):
        if self.pf is not None:
            pass_pct = self.pf.percent_passing
            offsets = ' '.join('{:.1f}'.format(pk.dist2cax) for pk in self.pf.pickets)
            results = [
                 f"Picket Fence Results: {pass_pct:2.1f}% Passed",
                 f"Median Error: {self.pf.abs_median_error:2.3f}mm",
                 f"Mean picket spacing: {self.pf.mean_picket_spacing:2.1f}mm",
                 f"Picket offsets from CAX (mm): {offsets}",
                 f"Max Error: {self.pf.max_error:2.3f}mm on Picket: {self.pf.max_error_picket}, Leaf: {self.pf.max_error_leaf}",
                 f"Failing leaves: {self.pf.failed_leaves()}"
            ]

            results = [html.P(r) for r in results]
            return results


analysis = Analysis()

layout = html.Div(children=[
    html.H1(children="Hello Picket Fence"),

    dcc.Upload(
        id="upload-data",
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
        multiple=False
    ),

    html.Button("Download", id="button-download-output", n_clicks=0),
    dcc.Download(id="download-output"),

    html.Div(id="output-data-upload"),

    html.Div([html.Img(id = "cur_plot", src="")], 
              id="plot_div")

    
])


def parse_content(contents, filename=None, date=None):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    return io.BytesIO(decoded)


@callback(
    Output("download-output", "data"),
    Input("button-download-output", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    if n_clicks > 0 and analysis.pf is not None:
        bytes_buffer = io.BytesIO()
        analysis.pf.publish_pdf(bytes_buffer)
        filename = "pylinac_picket_fence.pdf"
        if analysis.input_file is not None:
            filename = Path(analysis.input_file).stem + ".pdf"
        return dcc.send_bytes(bytes_buffer.getvalue(), filename=filename)


@callback(Output("output-data-upload", "children"),
          Output("cur_plot", "src"),
          Input("upload-data", "contents"),
          State("upload-data", "filename"),
          State("upload-data", "last_modified"))
def update_output(content, name, date):
    if content is not None:
        analysis.analyze(parse_content(content), name)
        children = [
            html.H5(f"File name: {name}"),
            # html.H5(f"Date: {date}"),
            html.Div(children=analysis.get_results())
        ]
        url = fig_to_uri(plot_analyzed_image(analysis.pf))
        return children, url
    return None, None
