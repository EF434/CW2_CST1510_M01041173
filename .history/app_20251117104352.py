import streamlit as st

st.title("Hello, Streamlit! 👋")
st.write("This is my very first Streamlit app.")

importpandasaspd

 df = pd.DataFrame({
"name": ["Alice", "Bob", "Charlie"],
"age": [25, 32, 29]
 })

st.dataframe(df)
