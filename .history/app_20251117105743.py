import streamlit as st
import pandas as pd

st.title("1. Basic Page Elements")
st.header("Headers and text")
st.subheader("This is a subheader")
st.caption("Small, grey caption text")

st.write("st.write` is very flexible – you can pass strings, numbers, dataframes, etc.")
st.text("Plain fixed-width text for code-like things.")
st.markdown("You can use **Markdown** here, including *italic* and `code`.")
