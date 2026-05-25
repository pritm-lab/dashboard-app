import streamlit as st
import pandas as pd

st.set_page_config(page_title="MIS Dashboard", layout="wide")
st.title("📊 MIS & Quality Dashboard")

# ---------------- LOAD DATA ----------------
df = pd.read_excel("Primary Analysis 042426.xlsx", sheet_name="Data")

# ---------------- CLEAN COLUMN NAMES ----------------
df.columns = (
    df.columns.astype(str)
    .str.replace("\n", "", regex=True)
    .str.replace("\t", "", regex=True)
    .str.replace("\r", "", regex=True)
    .str.strip()
)

# ---------------- FIND T/F COLUMN ----------------
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

# ================= FILTERS =================
st.sidebar.header("🔍 Filters")

df["Audited Date"] = pd.to_datetime(df["Audited Date"]).dt.date

Date = st.sidebar.multiselect(
    "Date",
    options=sorted(df["Audited Date"].dropna().unique()) if "Audited Date" in df.columns else []
)

account = st.sidebar.multiselect(
    "Account",
    options=sorted(df["Account_name"].dropna().unique()) if "Account_name" in df.columns else []
)

doctor = st.sidebar.multiselect(
    "Doctor",
    options=sorted(df["Doctor"].dropna().unique()) if "Doctor" in df.columns else []
)

user = st.sidebar.multiselect(
    "User",
    options=sorted(df["Responsible_User_Name"].dropna().unique()) if "Responsible_User_Name" in df.columns else []
)

status_filter = st.sidebar.multiselect(
    "Responsible User Status",
    options=sorted(df["Responsible_User_Status"].dropna().unique()) if "Responsible_User_Status" in df.columns else []
)

initial_filter = st.sidebar.multiselect(
    "Initial",
    options=sorted(df["Initial"].dropna().unique()) if "Initial" in df.columns else []
)

tf_filter = st.sidebar.multiselect(
    "T/F",
    options=sorted(df[tf_col].dropna().unique()) if tf_col else [],
    default=["false"] if tf_col else []
)

# ================= APPLY FILTERS =================
filtered_df = df.copy()

if Date:
    filtered_df = filtered_df[filtered_df["Audited Date"].isin(account)]
if account:
    filtered_df = filtered_df[filtered_df["Account_name"].isin(account)]
if doctor:
    filtered_df = filtered_df[filtered_df["Doctor"].isin(doctor)]
if user:
    filtered_df = filtered_df[filtered_df["Responsible_User_Name"].isin(user)]
if status_filter:
    filtered_df = filtered_df[filtered_df["Responsible_User_Status"].isin(status_filter)]
if initial_filter:
    filtered_df = filtered_df[filtered_df["Initial"].isin(initial_filter)]
if tf_col and tf_filter:
    filtered_df = filtered_df[filtered_df[tf_col].isin(tf_filter)]

# ================= KPI =================
kpi_df = filtered_df.copy()

total_audited_files = len(kpi_df)

go_files = len(kpi_df[kpi_df["NoGo/Go"] == "go"]) if "NoGo/Go" in kpi_df.columns else 0
nogo_files = len(kpi_df[kpi_df["NoGo/Go"] == "nogo"]) if "NoGo/Go" in kpi_df.columns else 0

go_percent = round((go_files / total_audited_files) * 100, 2) if total_audited_files else 0
nogo_percent = round((nogo_files / total_audited_files) * 100, 2) if total_audited_files else 0

st.subheader("📌 KPI Summary")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Audited Files", total_audited_files)
col2.metric("Go Files", go_files)
col3.metric("Go %", f"{go_percent}%")
col4.metric("NoGo Files", nogo_files)
col5.metric("NoGo %", f"{nogo_percent}%")

# ================= PIVOTS =================
col1, col2, col3 = st.columns(3)

# ================= USER WISE =================
with col1:
    st.subheader("👤 User Wise")

    if "Responsible_User_Name" in filtered_df.columns:

        user_pivot = pd.pivot_table(
            filtered_df,
            index="Responsible_User_Name",
            columns="NoGo/Go",
            values="Account_name",
            aggfunc="count",
            fill_value=0
        ).reset_index()

        user_pivot.columns.name = None
        user_pivot["go"] = user_pivot.get("go", 0)
        user_pivot["nogo"] = user_pivot.get("nogo", 0)

        user_pivot = user_pivot.rename(columns={
            "Responsible_User_Name": "User",
            "go": "Go",
            "nogo": "NoGo"
        })

        user_pivot["Total"] = user_pivot["Go"] + user_pivot["NoGo"]

        user_pivot["NoGo%"] = (
            user_pivot["NoGo"] / user_pivot["Total"] * 100
        ).round(2)

        user_pivot = user_pivot.sort_values(by="NoGo%", ascending=False)

        st.dataframe(user_pivot, hide_index=True, use_container_width=True)


# ================= INITIAL WISE =================
with col2:
    st.subheader("🏥 Initial Wise")

    if "Initial" in filtered_df.columns:

        initial_pivot = pd.pivot_table(
            filtered_df,
            index="Initial",
            columns="NoGo/Go",
            values="Account_name",
            aggfunc="count",
            fill_value=0
        ).reset_index()

        initial_pivot.columns.name = None
        initial_pivot["go"] = initial_pivot.get("go", 0)
        initial_pivot["nogo"] = initial_pivot.get("nogo", 0)

        initial_pivot = initial_pivot.rename(columns={
            "go": "Go",
            "nogo": "NoGo"
        })

        initial_pivot["Total"] = initial_pivot["Go"] + initial_pivot["NoGo"]

        initial_pivot["NoGo%"] = (
            initial_pivot["NoGo"] / initial_pivot["Total"] * 100
        ).round(2)

        initial_pivot = initial_pivot.sort_values(by="NoGo%", ascending=False)

        st.dataframe(initial_pivot, hide_index=True, use_container_width=True)


# ================= DOCTOR WISE =================
with col3:
    st.subheader("🩺 Doctor Wise")

    if "Doctor" in filtered_df.columns:

        doctor_pivot = pd.pivot_table(
            filtered_df,
            index="Doctor",
            columns="NoGo/Go",
            values="Account_name",
            aggfunc="count",
            fill_value=0
        ).reset_index()

        doctor_pivot.columns.name = None
        doctor_pivot["go"] = doctor_pivot.get("go", 0)
        doctor_pivot["nogo"] = doctor_pivot.get("nogo", 0)

        doctor_pivot = doctor_pivot.rename(columns={
            "go": "Go",
            "nogo": "NoGo"
        })

        doctor_pivot["Total"] = doctor_pivot["Go"] + doctor_pivot["NoGo"]

        doctor_pivot["NoGo%"] = (
            doctor_pivot["NoGo"] / doctor_pivot["Total"] * 100
        ).round(2)

        doctor_pivot = doctor_pivot.sort_values(by="NoGo%", ascending=False)

        st.dataframe(doctor_pivot, hide_index=True, use_container_width=True)
