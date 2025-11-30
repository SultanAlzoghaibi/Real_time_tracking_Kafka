import os
from datetime import datetime

import psycopg2
import pandas as pd
from dotenv import load_dotenv

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go


# -------------------------------------------------------------------
# DB connection settings
# -------------------------------------------------------------------
# PostgreSQL setup (trades DB that your consumer writes into).
load_dotenv()

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGUSER = os.getenv("PGUSER", "sultanalzoghaibi")
PGPASS = os.getenv("PGPASSWORD", "")
PGDB   = os.getenv("PGDATABASE", "trades")

DSN = f"host={PGHOST} port={PGPORT} dbname={PGDB} user={PGUSER} password={PGPASS}"


# -------------------------------------------------------------------
# Pull trade data from PostgreSQL for a given symbol
# -------------------------------------------------------------------
def fetch_trades(symbol: str, limit: int = 200) -> pd.DataFrame:
    """
    Returns a DataFrame with the most recent trades for the given symbol.
    Reads from the public.trades table that your consumer populates.
    """
    conn = psycopg2.connect(DSN)
    try:
        query = """
            SELECT
                trade_time,
                price,
                quantity
            FROM trades
            WHERE symbol = %s
            ORDER BY trade_time DESC
            LIMIT %s;
        """
        df = pd.read_sql(query, conn, params=(symbol, limit))
    finally:
        conn.close()

    if not df.empty:
        df["trade_time"] = pd.to_datetime(df["trade_time"])
        # we want time moving forward on the x-axis
        df = df.sort_values("trade_time")

    return df


# -------------------------------------------------------------------
# Pull recent alerts for a given symbol
# -------------------------------------------------------------------
def fetch_alerts(symbol: str, limit: int = 5):
    """
    Returns a list of (created_at, message) tuples from the alerts table
    for the given symbol, most recent first.

    Assumes alerts table:
        id SERIAL PRIMARY KEY
        symbol TEXT
        message TEXT
        created_at TIMESTAMPTZ DEFAULT NOW()
    """
    conn = psycopg2.connect(DSN)
    try:
        query = """
            SELECT created_at, message
            FROM alerts
            WHERE symbol = %s
            ORDER BY created_at DESC
            LIMIT %s;
        """
        with conn.cursor() as cur:
            cur.execute(query, (symbol, limit))
            rows = cur.fetchall()
    finally:
        conn.close()

    return rows


# -------------------------------------------------------------------
# Dashboard setup
# -------------------------------------------------------------------
app = Dash(__name__)
app.title = "Live Crypto Dashboard"

# Same symbols as in your producer / consumer pipeline
DEFAULT_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "TRXUSDT",
    "LINKUSDT",
]

app.layout = html.Div(
    style={"fontFamily": "Georgia, serif", "padding": "20px", "backgroundColor": "#B5EFEF"},
    children=[
        html.H1(
            "Crypto Live Dashboard",
            style={"textAlign": "center", "marginBottom": "20px"},
        ),

        # Symbol selector
        dcc.Dropdown(
            id="symbol-dropdown",
            options=[{"label": s, "value": s} for s in DEFAULT_SYMBOLS],
            value="BTCUSDT",
            clearable=False,
            style={"width": "300px", "margin": "0 auto 20px auto"},
        ),

        # Slider: how many recent trades we show
        html.Div(
            style={"textAlign": "center", "marginBottom": "10px"},
            children=[
                html.Span("Show last "),
                dcc.Slider(
                    id="points-slider",
                    min=50,
                    max=400,
                    step=50,
                    value=200,
                    marks={i: str(i) for i in range(50, 401, 50)},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
                html.Div(id="points-label", style={"marginTop": "8px"}),
            ],
        ),

        # Main price chart
        dcc.Graph(
            id="price-chart",
            style={"height": "500px"},
        ),

        # Recent alerts section
        html.Div(
            style={"maxWidth": "900px", "margin": "20px auto"},
            children=[
                html.H3("Recent alerts", style={"textAlign": "center"}),
                html.Ul(
                    id="alerts-list",
                    style={
                        "listStyleType": "none",
                        "padding": 0,
                        "margin": 0,
                        "textAlign": "left",
                    },
                ),
            ],
        ),

        # Auto-refresh timer → every 0.5 seconds (500 ms)
        dcc.Interval(
            id="update-interval",
            interval=500,  # 500 milliseconds = 0.5 s
            n_intervals=0,
        ),
    ],
)


# -------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------
@app.callback(
    Output("points-label", "children"),
    Input("points-slider", "value"),
)
def update_points_label(n_points):
    return f"Currently showing last {n_points} trades."


@app.callback(
    Output("price-chart", "figure"),
    [
        Input("symbol-dropdown", "value"),
        Input("points-slider", "value"),
        Input("update-interval", "n_intervals"),
    ],
)
def update_chart(selected_symbol, n_points, n_intervals):
    """
    Every 0.5 s:
      - pull fresh trades from DB
      - redraw chart with price + MA(10)
    """
    df = fetch_trades(selected_symbol, limit=n_points)

    if df.empty:
        return go.Figure(
            layout=go.Layout(
                title=f"{selected_symbol} – no data found",
                xaxis=dict(title="Time"),
                yaxis=dict(title="Price (USDT)"),
            )
        )

    # Price trace
    price_trace = go.Scatter(
        x=df["trade_time"],
        y=df["price"],
        mode="lines+markers",
        name="Price",
    )

    traces = [price_trace]

    # Simple 10-point moving average
    if len(df) >= 10:
        df["ma_10"] = df["price"].rolling(window=10).mean()
        ma_trace = go.Scatter(
            x=df["trade_time"],
            y=df["ma_10"],
            mode="lines",
            name="MA(10)",
            line=dict(dash="dash"),
        )
        traces.append(ma_trace)

    layout = go.Layout(
        title=f"{selected_symbol} – last {len(df)} trades",
        xaxis=dict(title="Trade Time"),
        yaxis=dict(title="Price (USDT)"),
        hovermode="x unified",
        margin=dict(l=60, r=30, t=70, b=60),
        paper_bgcolor="#C0F6CE",
        plot_bgcolor="#CEE6F1",
        font=dict(color="black"),
    )

    return go.Figure(data=traces, layout=layout)


@app.callback(
    Output("alerts-list", "children"),
    [
        Input("symbol-dropdown", "value"),
        Input("update-interval", "n_intervals"),
    ],
)
def update_alerts(selected_symbol, n_intervals):
    """
    Every 0.5 s:
      - pull latest alerts for the selected symbol
      - render them as a simple list under the chart
    """
    rows = fetch_alerts(selected_symbol, limit=8)

    if not rows:
        return [html.Li("No alerts yet for this symbol.", style={"color": "gray"})]

    items = []
    for created_at, message in rows:
        # created_at is a datetime; format to something short
        if isinstance(created_at, datetime):
            ts_str = created_at.strftime("%H:%M:%S")
        else:
            ts_str = str(created_at)
        items.append(
            html.Li(
                f"[{ts_str}] {message}",
                style={"marginBottom": "4px"},
            )
        )

    return items


# -------------------------------------------------------------------
# Run app
# -------------------------------------------------------------------
if __name__ == "__main__":
    # debug=False → no Dash dev toolbar
    app.run(debug=False)
