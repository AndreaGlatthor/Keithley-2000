import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
import threading
import os

# Filenames all start with the date and time in the format 2025-09-17_14-23
now_str = datetime.now().strftime("%Y-%m-%d_%H-%M")

# Calibration constants for the three channels
CAL_FACTORS = [12.45, 12.3151, 12.9117]


def run_measurement(filenames, interval_seconds, weights):
    import pyvisa
    import time

    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    print("Available VISA resources:", resources)
    if not resources:
        print("No VISA resources found!")
        return

    resource_str = resources[0]
    print(f"Connecting to {resource_str} ...")
    instrument = rm.open_resource(resource_str)
    instrument.baud_rate = 9600
    instrument.data_bits = 8
    instrument.stop_bits = pyvisa.constants.StopBits.one
    instrument.parity = pyvisa.constants.Parity.none
    instrument.flow_control = pyvisa.constants.ControlFlow.none
    instrument.timeout = 5000
    instrument.write_termination = "\r"
    instrument.read_termination = "\r"
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
    #    instrument.write("ROUT:OPEN:ALL")
    #    instrument.write("ROUT:CLOS (@1)")
    #    result = instrument.query("READ?")
    #    print("Measurement result:", result)

    try:
        start_time = time.time()
        while not stop_flag.is_set():
            for channel in range(1, 4):
                if stop_flag.is_set():
                    break
                # Check if a weight is specified for this channel
                if weights[channel - 1] is None:
                    continue  # No weight → no measurement/no writing
                try:
                    instrument.write("*SRE 1")
                    instrument.write("SENS:FUNC 'Volt:DC'")
                    instrument.write("ROUT:OPEN:ALL")
                    instrument.write(f"ROUT:CLOS (@{channel})")
                    time.sleep(0.05)
                    result = instrument.query("READ?")

                    try:
                        value = float(result.strip())
                    except Exception:
                        value = None

                    if value is not None:
                        calibrated = value * CAL_FACTORS[channel - 1]
                        try:
                            normed = calibrated / weights[channel - 1]
                        except Exception:
                            normed = ""
                    else:
                        normed = ""
                        calibrated = ""

                    elapsed_seconds = time.time() - start_time
                    elapsed_hours = elapsed_seconds / 3600.0

                    with open(filenames[channel - 1], "a") as f:
                        f.write(
                            f"{elapsed_hours:.6f}, {result.strip()}, {calibrated if calibrated != '' else ''}, {normed}\n"
                        )
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
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                # Filenames stacked (left)
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Filename Channel 1"
                                                        ),
                                                        dcc.Input(
                                                            id="filename1",
                                                            type="text",
                                                            value=f"{now_str}-1.csv",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label(
                                                            "Filename Channel 2"
                                                        ),
                                                        dcc.Input(
                                                            id="filename2",
                                                            type="text",
                                                            value=f"{now_str}-2.csv",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label(
                                                            "Filename Channel 3"
                                                        ),
                                                        dcc.Input(
                                                            id="filename3",
                                                            type="text",
                                                            value=f"{now_str}-3.csv",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                    ],
                                                    width=7,
                                                ),
                                                # Weights stacked (right)
                                                dbc.Col(
                                                    [
                                                        html.Label("Weight 1 (g)"),
                                                        dcc.Input(
                                                            id="weight1",
                                                            type="number",
                                                            step="0.001",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label("Weight 2 (g)"),
                                                        dcc.Input(
                                                            id="weight2",
                                                            type="number",
                                                            step="0.001",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                        html.Label("Weight 3 (g)"),
                                                        dcc.Input(
                                                            id="weight3",
                                                            type="number",
                                                            step="0.001",
                                                            className="mb-2",
                                                            style={"width": "100%"},
                                                        ),
                                                    ],
                                                    width=5,
                                                ),
                                            ]
                                        ),
                                        html.Hr(),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Measurement point spacing (s)",
                                                            style={
                                                                "marginRight": "10px"
                                                            },
                                                        ),
                                                        dcc.Input(
                                                            id="interval-input",
                                                            type="number",
                                                            value=20,
                                                            min=10,
                                                            step=10,
                                                            className="mb-3",
                                                            style={"width": "20%"},
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Hr(),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Run",
                                                        id="run-button",
                                                        color="success",
                                                        className="mt-2",
                                                        n_clicks=0,
                                                        style={
                                                            "width": "100%",
                                                            "opacity": "1",
                                                        },
                                                        disabled=False,
                                                    )
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Stop",
                                                        id="stop-button",
                                                        color="danger",
                                                        className="mt-2",
                                                        n_clicks=0,
                                                        style={
                                                            "width": "100%",
                                                            "opacity": "0.2",
                                                        },  # opacity 0.2 also in layout
                                                        disabled=True,  # Disabled before start
                                                    )
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            id="measurement-indicator",
                                            className="mt-3",
                                            style={
                                                "fontWeight": "bold",
                                                "fontSize": "1.2em",
                                            },
                                        ),
                                    ]
                                )
                            ]
                        )
                    ],
                    width=4,
                ),
                # Right column: Graph
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
        dcc.Store(id="measurement-running", data=False),  # Status flag
        dcc.Store(id="stop-requested", data=False),
        dcc.Interval(
            id="graph-update-interval", interval=3000, n_intervals=0  # interval in ms, update every 3 seconds
        ), 
    ],
    fluid=False,
    style={
        "maxWidth": "1200px",
        "margin": "auto",
    },
)


# Helper function: Read current measurement data from files
def read_measurement_data(filenames):
    data = []
    for fname in filenames:
        times = []
        normed = []
        if os.path.exists(fname):
            with open(fname, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 4:
                        try:
                            t = float(parts[0])
                            n = float(parts[3])
                            times.append(t)
                            normed.append(n)
                        except Exception:
                            continue
        data.append((times, normed))
    return data


# Global variable for thread and stop flag
measurement_thread = None
stop_flag = threading.Event()


@app.callback(
    [
        Output("run-status", "children"),
        Output("run-button", "disabled"),
        Output("run-button", "style"),
        Output("stop-button", "disabled"),
        Output("stop-button", "style"),
        Output("measurement-running", "data"),
        Output("stop-requested", "data"),
        Output("measurement-indicator", "children"),
        Output("measurement-indicator", "style"),
    ],
    [Input("run-button", "n_clicks"), Input("stop-button", "n_clicks")],
    [
        State("filename1", "value"),
        State("filename2", "value"),
        State("filename3", "value"),
        State("interval-input", "value"),
        State("weight1", "value"),
        State("weight2", "value"),
        State("weight3", "value"),
        State("measurement-running", "data"),
        State("stop-requested", "data"),
    ],
    prevent_initial_call=True,
)
def control_measurement(
    run_clicks,
    stop_clicks,
    filename1,
    filename2,
    filename3,
    interval,
    w1,
    w2,
    w3,
    running,
    stop_requested,
):
    global measurement_thread, stop_flag

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Default styles
    run_style_active = {"width": "100%", "opacity": "1"}
    run_style_disabled = {"width": "100%", "opacity": "0.2"}
    stop_style_active = {"width": "100%", "opacity": "1"}
    stop_style_disabled = {"width": "100%", "opacity": "0.2"}
    indicator_style_running = {
        "color": "#28a745",
        "fontWeight": "bold",
        "fontSize": "1.2em",
    }
    indicator_style_idle = {
        "color": "#000000",
        "fontWeight": "normal",
        "fontSize": "1.2em",
    }

    if button_id == "run-button" and not running:
        stop_flag.clear()

        def parse_weight(val):
            try:
                return float(str(val).replace(",", "."))
            except Exception:
                return None

        weights = [parse_weight(w1), parse_weight(w2), parse_weight(w3)]
        filenames = [filename1, filename2, filename3]
        measurement_thread = threading.Thread(
            target=run_measurement, args=(filenames, interval - 1, weights)
        )
        measurement_thread.daemon = True
        measurement_thread.start()
        return (
            "",
            True,
            run_style_disabled,
            False,  # Stop button now active
            stop_style_active,
            True,
            False,
            "● Measurement in progress",
            indicator_style_running,
        )

    if button_id == "stop-button" and running:
        stop_flag.set()
        return (
            "",
            False,
            run_style_active,
            True,  # Stop button disabled again
            stop_style_disabled,
            False,
            True,
            "",
            indicator_style_idle,
        )

    if running:
        return (
            "",
            True,
            run_style_disabled,
            False,  # Stop button active during measurement
            stop_style_active,
            True,
            False,
            "● Measurement in progress",
            indicator_style_running,
        )
    return (
        "",
        False,
        run_style_active,
        True,  # Stop button remains disabled before start
        stop_style_disabled,
        False,
        False,
        "",
        indicator_style_idle,
    )


@app.callback(
    Output("main-graph", "figure"),
    [
        Input("graph-update-interval", "n_intervals"),
        State("filename1", "value"),
        State("filename2", "value"),
        State("filename3", "value"),
    ],
)
def update_graph(n, filename1, filename2, filename3):
    filenames = [filename1, filename2, filename3]
    data = read_measurement_data(filenames)
    fig = go.Figure()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    # Find the minimum of all normed values
    all_normed = []
    for times, normed in data:
        all_normed.extend(normed)
    y_min = min(all_normed) if all_normed else 0

    for i, (times, normed) in enumerate(data):
        if times and normed:
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=normed,
                    mode="lines+markers",
                    name=f"Channel {i+1}",
                    line=dict(color=colors[i]),
                )
            )
    fig.update_layout(
        xaxis=dict(
            title="Time (h)",
            range=[0, None],  # x-axis starts at 0
            showline=True,
            linecolor="black",
            linewidth=2,
            mirror=False,  # Only axis at x=0
        ),
        yaxis=dict(
            title="Heat flow (mW/g)",
            range=[y_min, None],  # y-axis starts at minimum
            showline=True,
            linecolor="black",
            linewidth=2,
            mirror=False,  # Only axis at y=0
        ),
        template="plotly_white",
        legend_title="Channel",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
