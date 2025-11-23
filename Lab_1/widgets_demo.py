import streamlit as st

st.title("2. Basic Widgets Demo")

st.header("Buttons & text inputs")
name = st.text_input("What is your name?")
if st.button("Say hello"):
  if name:
    st.success(f"Hello, {name} 👋 ")
  else:
    st.warning("Please enter your name first.")

st.divider()
st.header("Numeric inputs")

age = st.number_input("Your age", min_value=0, max_value=120,
value=25)
st.write("You entered age:", age)
st.slider("Pick a value", min_value=0, max_value=100, value=50,
key="slider_example")

st.divider()

st.header("Selection widgets")
color = st.selectbox("Favourite colour", ["Red", "Green",
"Blue"])
options = st.multiselect("Choose some fruits", ["Apple",
"Banana", "Orange", "Grapes"])
st.write("Colour:", color)
st.write("Fruits:", options)

st.divider()

st.header("Booleans and dates")
agree = st.checkbox("I agree to the terms")
if agree:
   st.info("Thanks for agreeing. ")
   
date = st.date_input("Pick a date")
st.write("Chosen date:", date)
