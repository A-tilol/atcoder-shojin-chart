import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

import chart
import logger

log = logger.get_logger(__name__, level=10)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

input_style = {"width": "400px"}
form_style = {"margin-top": "1rem"}


app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        html.Div(
            children="""
        Dash: A web application framework for your data.
    """
        ),
        html.Div(
            [
                dbc.Label("UserID", html_for="user-id-input"),
                dbc.Input(
                    id="user-id-input",
                    value="",
                    type="text",
                    placeholder="chokudai",
                    style=input_style,
                ),
            ],
            style=form_style,
        ),
        html.Div(
            [
                dbc.Label("RivalIDs", html_for="rival-ids-input"),
                dbc.Input(
                    id="rival-ids-input",
                    value="",
                    type="text",
                    placeholder="id1, id2, ...",
                    style=input_style,
                ),
            ],
            style=form_style,
        ),
        html.Div(
            [
                dbc.Label("Period (days)", html_for="Period-input"),
                dbc.Input(
                    id="period-input",
                    value=90,
                    type="number",
                    min=10,
                    step=10,
                    placeholder="90",
                    style=input_style,
                ),
            ],
            style=form_style,
        ),
        html.Div(
            dbc.Button("Create Chart!", id="create-chart-btn", n_clicks=0),
            style=form_style,
        ),
        html.Div(
            dcc.Graph(
                id="shojin-chart",
                figure={},
                config={"displayModeBar": False},
            ),
            style=form_style,
        ),
        html.Div(
            [
                dbc.Label("Metrics"),
                dbc.RadioItems(
                    ["スコア", "AC数", "レーティング"],
                    "スコア",
                    inline=True,
                ),
            ],
            style=form_style,
        ),
    ],
    style={"margin": "20px"},
)


@callback(
    Output(component_id="shojin-chart", component_property="figure"),
    Output(component_id="shojin-chart", component_property="style"),
    Input(component_id="create-chart-btn", component_property="n_clicks"),
    State(component_id="user-id-input", component_property="value"),
    State(component_id="rival-ids-input", component_property="value"),
    State(component_id="period-input", component_property="value"),
)
def update_chart(n_clicks: int, user_id: str, rival_ids: str, period: int):
    log.debug((user_id, rival_ids))
    if user_id == "":
        return {}, {"display": "none"}

    users = [user_id]
    if rival_ids:
        users += rival_ids.replace(" ", "").split(",")

    return chart.draw_chart(users, period), {"display": "block"}


if __name__ == "__main__":
    app.run(debug=True)
