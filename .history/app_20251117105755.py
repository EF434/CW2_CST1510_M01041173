import streamlit as st
import pandas as pd

st.title("1. Basic Page Elements")
st.header("Headers and text")
st.subheader("This is a subheader")
st.caption("Small, grey caption text")

st.write("st.write` is very flexible – you can pass strings, numbers, dataframes, etc.")
st.text("Plain fixed-width text for code-like things.")
st.markdown("You can use **Markdown** here, including *italic* and `code`.")

st.divider()
st.header("Display data")
df = pd.DataFrame({
 "name": ["Alice", "Bob", "Charlie"],
 "age": [25, 32, 29]
})
st.write("Here is a small dataframe:")
st.dataframe(df) # scrollable, sortable table
st.divider()
st.header("Images")
st.write("You can show images from a URL or local file.")
st.image(
 "https://streamlit.io/images/brand/streamlit-logo-secondarycolormark-darktext.png",
 caption="Streamlit logo",
)
