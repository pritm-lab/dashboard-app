import streamlit as st
import pandas as pd

st.set_page_config(page_title="MIS Dashboard", layout="wide")

st.title("📊 MIS & Quality Dashboard")

df = pd.read_excel("data.xlsx", sheet_name="Data")

if uploaded_file:

    # ---------------- LOAD DATA ----------------
    df = pd.read_excel(uploaded_file, sheet_name="Data")

    # ---------------- CLEAN COLUMN NAMES ----------------
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", "", regex=True)
        .str.replace("\t", "", regex=True)
        .str.replace("\r", "", regex=True)
        .str.strip()
    )

    # ---------------- FIND T/F COLUMN SAFELY ----------------
    tf_col = None
    for col in df.columns:
        if "t/f" in col.lower().replace(" ", ""):
            tf_col = col
            break

    # ---------------- CLEAN DATA ----------------
    if tf_col:
        df[tf_col] = df[tf_col].astype(str).str.strip().str.lower()

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

    # ---------------- APPLY FILTERS ----------------
    filtered_df = df.copy()

    if account != "All" and "Account_name" in df.columns:
        filtered_df = filtered_df[filtered_df["Account_name"] == account]

    if doctor != "All" and "Doctor" in df.columns:
        filtered_df = filtered_df[filtered_df["Doctor"] == doctor]

    if user != "All" and "Responsible_User_Name" in df.columns:
        filtered_df = filtered_df[filtered_df["Responsible_User_Name"] == user]

    # ---------------- KPI LOGIC ----------------
    final_df = filtered_df.copy()

    if tf_col:
        df_false = final_df[
            final_df[tf_col].astype(str).str.contains("false|0|no", na=False)
        ]
    else:
        df_false = final_df.copy()

    total_audited_files = df_false["File_name"].nunique() if "File_name" in df_false.columns else 0

    go_files = df_false[
        df_false["NoGo/Go"].astype(str).str.strip().str.lower() == "go"
    ]["File_name"].nunique() if "NoGo/Go" in df_false.columns else 0

    nogo_files = df_false[
        df_false["NoGo/Go"].astype(str).str.strip().str.lower() == "nogo"
    ]["File_name"].nunique() if "NoGo/Go" in df_false.columns else 0

    go_percent = round((go_files / total_audited_files) * 100, 2) if total_audited_files else 0
    nogo_percent = round((nogo_files / total_audited_files) * 100, 2) if total_audited_files else 0

    # ---------------- KPI DISPLAY (FINAL ORDERED) ----------------
    st.subheader("📌 KPI Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Audited Files", total_audited_files)
    col2.metric("Go Files", go_files)
    col3.metric("Go %", go_percent)
    col4.metric("NoGo Files", nogo_files)
    col5.metric("NoGo %", nogo_percent)

    # ---------------- TABLE ----------------
    st.subheader("📄 Detailed Data Table")
    st.dataframe(final_df, use_container_width=True)

    # ---------------- CHARTS ----------------
    st.subheader("📊 Analysis")

    if "Doctor" in final_df.columns:
        st.bar_chart(final_df["Doctor"].value_counts())

    if "Account_name" in final_df.columns:
        st.bar_chart(final_df["Account_name"].value_counts())

    if "Responsible_User_Name" in final_df.columns:
        st.bar_chart(final_df["Responsible_User_Name"].value_counts())
