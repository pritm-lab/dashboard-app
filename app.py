import streamlit as st
import pandas as pd

st.set_page_config(page_title="MIS Dashboard", layout="wide")

st.title("📊 MIS & Quality Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ---------------- FILTER SIDEBAR ----------------
    st.sidebar.header("🔍 Filters")

    if "Account_name" in df.columns:
        account = st.sidebar.selectbox("Account", ["All"] + list(df["Account_name"].dropna().unique()))
    else:
        account = "All"

    if "Doctor" in df.columns:
        doctor = st.sidebar.selectbox("Doctor", ["All"] + list(df["Doctor"].dropna().unique()))
    else:
        doctor = "All"

    if "Responsible_User_Name" in df.columns:
        user = st.sidebar.selectbox("User", ["All"] + list(df["Responsible_User_Name"].dropna().unique()))
    else:
        user = "All"

    # ---------------- FILTER LOGIC ----------------
    filtered_df = df.copy()

    if account != "All":
        filtered_df = filtered_df[filtered_df["Account_name"] == account]

    if doctor != "All":
        filtered_df = filtered_df[filtered_df["Doctor"] == doctor]

    if user != "All":
        filtered_df = filtered_df[filtered_df["Responsible_User_Name"] == user]

    # ---------------- KPI SECTION ----------------
    st.subheader("📌 KPI Summary")

    col1, col2, col3, col4 = st.columns(4)

    total = len(filtered_df)

    go_count = len(filtered_df[filtered_df["NoGo/Go_2010"] == "Go"]) if "NoGo/Go_2010" in filtered_df.columns else 0
    nogo_count = len(filtered_df[filtered_df["NoGo/Go_2010"] == "NoGo"]) if "NoGo/Go_2010" in filtered_df.columns else 0

    accuracy = filtered_df["Accuracy_2010"].mean() if "Accuracy_2010" in filtered_df.columns else 0
    tat = filtered_df["TAT"].mean() if "TAT" in filtered_df.columns else 0

    col1.metric("Total Files", total)
    col2.metric("Go %", round((go_count/total)*100,2) if total else 0)
    col3.metric("Avg Accuracy", round(accuracy,2))
    col4.metric("Avg TAT", round(tat,2))

    # ---------------- MAIN TABLE ----------------
    st.subheader("📄 Detailed Data Table")
    st.dataframe(filtered_df, use_container_width=True)

    # ---------------- SUMMARY ----------------
    st.subheader("📊 Doctor / Account Summary")

    if "Doctor" in filtered_df.columns:
        st.write("### Doctor Wise Count")
        st.bar_chart(filtered_df["Doctor"].value_counts())

    if "Account_name" in filtered_df.columns:
        st.write("### Account Wise Count")
        st.bar_chart(filtered_df["Account_name"].value_counts())

    if "Responsible_User_Name" in filtered_df.columns:
        st.write("### User Wise Count")
        st.bar_chart(filtered_df["Responsible_User_Name"].value_counts())
