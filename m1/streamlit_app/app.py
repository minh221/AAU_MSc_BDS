import streamlit as st
from pages.a_main_page import fetch_and_clean_data
st.set_page_config(layout="wide")
st.title("Minh's Kiva Application")

df = fetch_and_clean_data()


st.write("🔍 See what the dataframe look like! ")
st.write("🎨 Then choose a page to view graph ")
# edited_df = st.data_editor(df)
st.write(df.head(100))