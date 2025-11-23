import streamlit as st
import pandas as pd
import numpy as np

st.title("3. Charts Demo")

st.header("Line, area, and bar charts")

# Fake time series data
data = pd.DataFrame(np.random.randn(20, 3),columns=["A", "B", "C"])

st.subheader("Line chart")
st.line_chart(data)

st.subheader("Area chart")
st.area_chart(data)

st.subheader("Bar chart")
st.bar_chart(data)

st.divider()

st.header("Scatter chart & map")

# Scatter chart
scatter_data = pd.DataFrame(
 np.random.randn(100, 3),
 columns=["x", "y", "size"]
)
st.subheader("Scatter chart")
st.scatter_chart(scatter_data, x="x", y="y", size="size")

# Map (requires lat/lon columns)
st.subheader("Map")
map_data = pd.DataFrame({
 "lat": 51.5 + np.random.randn(100) * 0.01,
 "lon": -0.12 + np.random.randn(100) * 0.01,
})
st.map(map_data)

