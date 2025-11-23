import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Layout Demo", layout="wide")

st.title("4️⃣ Layout Demo – Building a Simple Dashboard")

# ---- SIDEBAR ----
with st.sidebar:
  st.header("Controls")
  n_points = st.slider("Number of points", 10, 500, 100)
  show_table = st.checkbox("Show raw data")

# ---- MAIN CONTENT ----
st.header("Main Content")

# Create some random data
data = pd.DataFrame(
 np.random.randn(n_points, 3),
 columns=["Feature 1", "Feature 2", "Feature 3"]
)

# Use columns to split space
col1, col2 = st.columns(2)
with col1:
  st.subheader("Line chart")
  st.line_chart(data)

with col2:
  st.subheader("Bar chart")
  st.bar_chart(data)

# Optional table in an expander
with st.expander("See raw data"):
  if show_table:
    st.dataframe(data)
  else:
    st.info("Tick 'Show raw data' in the sidebar to see the table.")
