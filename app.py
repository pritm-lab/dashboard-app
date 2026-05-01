import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard App", layout="wide")

st.title("📊 MIS Dashboard")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("📄 Raw Data")
    st.dataframe(df)

    # Check required columns
    required_cols = ["Account", "Doctor", "User"]

    if all(col in df.columns for col in required_cols):

        # Filters
        account = st.selectbox("Select Account", df["Account"].unique())
        df1 = df[df["Account"] == account]

        doctor = st.selectbox("Select Doctor", df1["Doctor"].unique())
        df2 = df1[df1["Doctor"] == doctor]

        user = st.selectbox("Select User", df2["User"].unique())
        df3 = df2[df2["User"] == user]

        st.subheader("🎯 Filtered Data")
        st.dataframe(df3)

    else:
        st.error("Excel file ma 'Account', 'Doctor', 'User' columns hova joiye")
