
import pandas as pd
import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

conn = sqlite3.connect("honeywell.db")
df = pd.read_sql_query("SELECT * FROM hw_temp", conn)


fig = go.Figure()
fig.add_trace(go.Scatter(x=df["record_time"], y=df["indoor_temp"],
                    mode='lines',
                    name='Indoor (C°)'))
fig.add_trace(go.Scatter(x=df["record_time"], y=df["outdoor_temp"],
                    mode='lines',
                    name='Outdoor (C°)'))
fig.add_trace(go.Scatter(x=df["record_time"], y=df["outdoor_humidity"],
                    mode='lines', name='Humidity'))
fig.add_trace(go.Scatter(x=df["record_time"], y=df["is_heating"],
                    mode='lines', name='Is Heating'))

fig.show()

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True, use_reloader=False) 