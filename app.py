from dash import Dash, html, dcc
import dash

import matplotlib as mpl
mpl.use("Agg")

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),

	dash.page_container
])

if __name__ == "__main__":
	app.run_server(debug=True, host="0.0.0.0")