from pylinac import CatPhan504

import dash

from dash import Dash, html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State

from pylinac_ext.catphan import plot_analyzed_image, get_results
from dash_ext.matplotlib import fig_to_uri

import io
import base64
from pathlib import Path

dash.register_page(__name__)

class Analysis(object):
    def __init__(self):
        self.catphan = None
        self.input_file = None

    def analyze(self, dcm_file, filename=None):
        self.input_file = filename
        self.catphan = CatPhan504.from_zip(dcm_file)
        self.catphan.analyze()

    def get_results(self):
        results = get_results(self.catphan)
        return [html.P(r) for r in results]


analysis = Analysis()

layout = html.Div(children=[
    html.H1(children="Hello CatPhan504"),

    dcc.Upload(
        id="catphan-upload-data",
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

    html.Button("Download", id="catphan-button-download-output", n_clicks=0),
    dcc.Download(id="catphan-download-output"),

    html.Div(id="catphan-output-data-upload"),

    html.Div([html.Img(id = "catphan-cur_plot", src="")], 
              id="plot_div")

    
])


def parse_content(contents, filename=None, date=None):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    return io.BytesIO(decoded)


@callback(
    Output("catphan-download-output", "data"),
    Input("catphan-button-download-output", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    if n_clicks > 0 and analysis.catphan is not None:
        bytes_buffer = io.BytesIO()
        analysis.catphan.publish_pdf(bytes_buffer)
        filename = "pylinac_cbct.pdf"
        if analysis.input_file is not None:
            filename = Path(analysis.input_file).stem + ".pdf"
        return dcc.send_bytes(bytes_buffer.getvalue(), filename=filename)


@callback(Output("catphan-output-data-upload", "children"),
          Output("catphan-cur_plot", "src"),
          Input("catphan-upload-data", "contents"),
          State("catphan-upload-data", "filename"),
          State("catphan-upload-data", "last_modified"))
def update_output(content, name, date):
    if content is not None:
        analysis.analyze(parse_content(content), name)
        children = [
            html.H5(f"File name: {name}"),
            # html.H5(f"Date: {date}"),
            html.Div(children=analysis.get_results())
        ]
        url = fig_to_uri(plot_analyzed_image(analysis.catphan))
        return children, url
    return None, None
