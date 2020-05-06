
import pandas as pd
import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

conn = sqlite3.connect("honeywell.db")
df = pd.read_sql_query("SELECT * FROM hw_temp", conn)


fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Indoor", "Outdoor", "Humidity", "Is Heating"))
 
fig.add_trace(go.Scatter(x=df["record_time"], y=df["indoor_temp"],
                    mode='lines',
                    name='Indoor (C°)'), row=1, col=1)
fig.add_trace(go.Scatter(x=df["record_time"], y=df["outdoor_temp"],
                    mode='lines',
                    name='Outdoor (C°)'), row=2, col=1)
fig.add_trace(go.Scatter(x=df["record_time"], y=df["outdoor_humidity"],
                    mode='lines', name='Humidity'), row=1, col=2)
fig.add_trace(go.Scatter(x=df["record_time"], y=df["is_heating"],
                    mode='lines', name='Is Heating'), row=2, col=2)

 
 

fig.show()

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(id='hw-temp', figure=fig)
])

app.run_server(debug=True, host='0.0.0.0') 