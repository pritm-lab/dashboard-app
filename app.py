import streamlit as st
import pandas as pd

st.set_page_config(page_title="MIS Dashboard", layout="wide")

st.title("📊 MIS & Quality Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    # ---------------- LOAD DATA ----------------
    df = pd.read_excel(uploaded_file)

    # ---------------- CLEAN COLUMNS ----------------
    df.columns = df.columns.astype(str).str.strip().str.replace("\n", "").str.replace("\t", "")

    # ---------------- CLEAN DATA SAFELY ----------------
    if "T/F" in df.columns:
        df["T/F"] = df["T/F"].astype(str).str.strip().str.lower()

    if "NoGo/Go" in df.columns:
        df["NoGo/Go"] = df["NoGo/Go"].astype(str).str.strip().str.lower()

    # ---------------- FILTER SIDEBAR ----------------
    st.sidebar.header("🔍 Filters")

    account = st.sidebar.selectbox(
        "Account",
        ["All"] + list(df["Account_name"].dropna().unique())
    ) if "Account_name" in df.columns else "All"

    doctor = st.sidebar.selectbox(
        "Doctor",
        ["All"] + list(df["Doctor"].dropna().unique())
    ) if "Doctor" in df.columns else "All"

    user = st.sidebar.selectbox(
        "User",
        ["All"] + list(df["Responsible_User_Name"].dropna().unique())
    ) if "Responsible_User_Name" in df.columns else "All"

    # ---------------- FILTER APPLY ----------------
    filtered_df = df.copy()

    if account != "All":
        filtered_df = filtered_df[filtered_df["Account_name"] == account]

    if doctor != "All":
        filtered_df = filtered_df[filtered_df["Doctor"] == doctor]

    if user != "All":
        filtered_df = filtered_df[filtered_df["Responsible_User_Name"] == user]

    # ---------------- KPI FIX (REAL WORLD SAFE) ----------------
    df_false = filtered_df[
        filtered_df["T/F"].astype(str).str.strip().str.lower().isin(["false", "0", "no"])
    ] if "T/F" in filtered_df.columns else filtered_df

    total_audited_files = df_false["File_name"].nunique() if "File_name" in df_false.columns else 0

    go_files = df_false[
        df_false["NoGo/Go"].astype(str).str.strip().str.lower() == "go"
    ]["File_name"].nunique() if "NoGo/Go" in df_false.columns else 0

    nogo_files = df_false[
        df_false["NoGo/Go"].astype(str).str.strip().str.lower() == "nogo"
    ]["File_name"].nunique() if "NoGo/Go" in df_false.columns else 0

    go_percent = round((go_files / total_audited_files) * 100, 2) if total_audited_files else 0
    nogo_percent = round((nogo_files / total_audited_files) * 100, 2) if total_audited_files else 0

    # ---------------- KPI DISPLAY ----------------
    st.subheader("📌 KPI Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Audited Files", total_audited_files)
    col2.metric("Go Files", go_files)
    col3.metric("Go %", go_percent)
    col4.metric("NoGo %", nogo_percent)

    # ---------------- TABLE ----------------
    st.subheader("📄 Detailed Data Table")
    st.dataframe(filtered_df, use_container_width=True)

    # ---------------- CHARTS ----------------
    st.subheader("📊 Analysis")

    if "Doctor" in filtered_df.columns:
        st.write("Doctor Wise Count")
        st.bar_chart(filtered_df["Doctor"].value_counts())

    if "Account_name" in filtered_df.columns:
        st.write("Account Wise Count")
        st.bar_chart(filtered_df["Account_name"].value_counts())

    if "Responsible_User_Name" in filtered_df.columns:
        st.write("User Wise Count")
        st.bar_chart(filtered_df["Responsible_User_Name"].value_counts())
