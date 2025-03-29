import streamlit as st
import pandas as pd
from chirp_data import get_top_user_followers, get_top_user_chirps, get_latest_chirps

FOLLOWERS = get_top_user_followers()
CHIRPS = get_top_user_chirps()
LATEST = get_latest_chirps()

# Convert data to DataFrames
followers_df = pd.DataFrame(FOLLOWERS, columns=["User", "Followers"])
chirps_df = pd.DataFrame(CHIRPS, columns=["User", "Chirps"])
latest_chirps_df = pd.DataFrame(LATEST, columns=["Timestamp", "User", "Message"])

# Streamlit UI
st.title("🏆 Top 5 Users & Latest Chirps")

st.header("🏆 Top 5 par followers")
st.dataframe(followers_df.style.set_table_styles([
    {"selector": "th", "props": [("background-color", "#FFD700"), ("color", "black")]},
    {"selector": "td", "props": [("background-color", "#FFFACD")]}
]))

st.header("🏆 Top 5 par nombre de chirps")
st.dataframe(chirps_df.style.set_table_styles([
    {"selector": "th", "props": [("background-color", "#FF4500"), ("color", "white")]},
    {"selector": "td", "props": [("background-color", "#FFDAB9")]}
]))

st.header("🕒 Derniers chirps")
st.dataframe(latest_chirps_df.style.set_table_styles([
    {"selector": "th", "props": [("background-color", "#4682B4"), ("color", "white")]},
    {"selector": "td", "props": [("background-color", "#ADD8E6")]}
]))
