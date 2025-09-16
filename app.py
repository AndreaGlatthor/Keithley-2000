import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

# Aktuelles Datum im gewünschten Format
today_str = datetime.now().strftime("%Y-%m-%d")

app = dash.Dash(
    __name__, title="Keithley 2000 Monitor", external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H2("Keithley 2000 Monitor", className="text-center my-4"),
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                # Linke Spalte: Input-Bereich
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                # Dateinamen untereinander (links)
                                                dbc.Col(
                                                    [
                                                        html.Label("Dateiname 1"),
                                                        dcc.Input(
                                                            id="filename1",
                                                            type="text",
                                                            value=f"{today_str}-1.csv",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label("Dateiname 2"),
                                                        dcc.Input(
                                                            id="filename2",
                                                            type="text",
                                                            value=f"{today_str}-2.csv",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label("Dateiname 3"),
                                                        dcc.Input(
                                                            id="filename3",
                                                            type="text",
                                                            value=f"{today_str}-3.csv",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                # Einwaagen untereinander (rechts)
                                                dbc.Col(
                                                    [
                                                        html.Label("Einwaage 1"),
                                                        dcc.Input(
                                                            id="weight1",
                                                            type="number",
                                                            step="0.001",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label("Einwaage 2"),
                                                        dcc.Input(
                                                            id="weight2",
                                                            type="number",
                                                            step="0.001",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label("Einwaage 3"),
                                                        dcc.Input(
                                                            id="weight3",
                                                            type="number",
                                                            step="0.001",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                        html.Hr(),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Messpunktabstand (s)"
                                                        ),
                                                        dcc.Input(
                                                            id="interval-input",
                                                            type="number",
                                                            value=20,
                                                            min=20,
                                                            step=10,
                                                            className="mb-3",
                                                            style={"width": "100%"},
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Run",
                                                        id="run-button",
                                                        color="success",
                                                        className="mt-2",
                                                        n_clicks=0,
                                                        style={"width": "100%"},
                                                    )
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    width=4,
                ),
                # Rechte Spalte: Graph
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [dcc.Graph(id="main-graph", figure=go.Figure())]
                                )
                            ]
                        )
                    ],
                    width=8,
                ),
            ]
        ),
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run(debug=True)
