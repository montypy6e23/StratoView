import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="StratoView", layout="wide")

# -----------------------------
# TITLE
# -----------------------------
st.title("🌦 StratoView")
st.markdown("Live Weather & Air Traffic Map")

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.header("Controls")

altitude_range = st.sidebar.slider(
    "Altitude Range (meters)",
    min_value=0,
    max_value=40000,
    value=(0, 40000),
)

refresh = st.sidebar.button("🔄 Refresh Data")

# -----------------------------
# FETCH AIRCRAFT DATA
# -----------------------------
@st.cache_data(ttl=10)
def get_flights():
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)

    if response.status_code != 200:
        return pd.DataFrame()

    data = response.json()

    flights = []
    for state in data.get("states", []):
        if state[5] is None or state[6] is None:
            continue

        flights.append({
            "callsign": state[1].strip() if state[1] else "N/A",
            "lon": state[5],
            "lat": state[6],
            "altitude": state[7] if state[7] else 0,
            "velocity": state[9] if state[9] else 0,
        })

    df = pd.DataFrame(flights)
    return df


df = get_flights()

# -----------------------------
# FILTER DATA
# -----------------------------
if not df.empty:
    df = df[
        (df["altitude"] >= altitude_range[0]) &
        (df["altitude"] <= altitude_range[1])
    ]

# -----------------------------
# MAP VIEW STATE
# -----------------------------
view_state = pdk.ViewState(
    latitude=39.5,
    longitude=-98.35,
    zoom=4,
    pitch=45,
)

# -----------------------------
# AIRCRAFT LAYER
# -----------------------------
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[lon, lat]",
    get_radius=8000,
    pickable=True,
)

# -----------------------------
# TOOLTIP
# -----------------------------
tooltip = {
    "html": "<b>Callsign:</b> {callsign} <br/>"
            "<b>Altitude:</b> {altitude} m <br/>"
            "<b>Speed:</b> {velocity} m/s",
    "style": {"backgroundColor": "black", "color": "white"}
}

# -----------------------------
# RENDER MAP
# -----------------------------
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip
))

# -----------------------------
# FOOTER INFO
# -----------------------------
st.markdown(f"✈️ Aircraft displayed: {len(df)}")
