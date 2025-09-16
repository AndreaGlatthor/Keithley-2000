import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
import threading

import pyvisa
import time

today_str = datetime.now().strftime("%Y-%m-%d")


# --- Messroutine als Funktion ---
def run_measurement(filenames, interval_seconds):
    rm = pyvisa.ResourceManager()
    resource_str = "ASRL1::INSTR"  # ASRL1 usually maps to COM1
    instrument = rm.open_resource(resource_str)

    # Set serial communication parameters
    instrument.baud_rate = 9600
    instrument.data_bits = 8
    instrument.stop_bits = pyvisa.constants.StopBits.one
    instrument.parity = pyvisa.constants.Parity.none
    instrument.flow_control = pyvisa.constants.ControlFlow.none
    instrument.timeout = 5000  # 5 seconds

    instrument.write_termination = "\r"
    instrument.read_termination = "\r"

    # --- Send initialization and measurement commands ---
    instrument.write("*RST")
    instrument.write("*WAI")
    instrument.write("SRE 1")
    instrument.write("SYST:RWL")
    instrument.write("SENS:FUNC 'Volt:DC'")
    instrument.write("SYST:AZER:STAT 0")
    instrument.write("SENS:VOLT:DC:AVER:STAT 0")
    instrument.write("SENS:VOLT:DC:NPLC 10")
    instrument.write("SENS:VOLT:DC:RANG:AUTO 1")
    instrument.write("SENS:VOLT:DC:DIG 7")
    instrument.write("SENS:Volt:DC:REF:STAT 0")
    instrument.write("ROUT:OPEN:ALL")
    instrument.write("ROUT:CLOS (@1)")
    result = instrument.query("READ?")
    print("Measurement result:", result)

    try:
        start_time = time.time()
        while True:
            for channel in range(1, 4):
                try:
                    instrument.write("*SRE 1")
                    instrument.write("SENS:FUNC 'Volt:DC'")
                    instrument.write("ROUT:OPEN:ALL")
                    instrument.write(f"ROUT:CLOS (@{channel})")
                    time.sleep(0.05)
                    result = instrument.query("READ?")

                    elapsed_seconds = time.time() - start_time
                    elapsed_hours = elapsed_seconds / 3600.0

                    with open(filenames[channel - 1], "a") as f:
                        f.write(f"{elapsed_hours:.6f}, {result.strip()}\n")
                except Exception as e:
                    print(f"Error with channel {channel}: {e}")
            time.sleep(interval_seconds)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        instrument.write("ROUT:CLOS:ALL")
        instrument.close()


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
        html.Div(id="run-status", className="mt-3", style={"fontWeight": "bold"}),
    ],
    fluid=True,
)


@app.callback(
    Output("run-status", "children"),
    Input("run-button", "n_clicks"),
    [
        State("filename1", "value"),
        State("filename2", "value"),
        State("filename3", "value"),
        State("interval-input", "value"),
    ],
    prevent_initial_call=True,
)
def start_measurement(n_clicks, filename1, filename2, filename3, interval):
    if n_clicks > 0:
        # Starte Messroutine in separatem Thread, damit das UI nicht blockiert
        filenames = [filename1, filename2, filename3]
        thread = threading.Thread(
            target=run_measurement, args=(filenames, interval - 1)
        )
        thread.daemon = True
        thread.start()
        return "Messung läuft..."
    return ""


if __name__ == "__main__":
    app.run(debug=True)
