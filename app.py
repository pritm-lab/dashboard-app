import streamlit as st
import pandas as pd

st.set_page_config(page_title="MIS Dashboard", layout="wide")

st.title("📊 MIS & Quality Dashboard")

# ---------------- LOAD DATA ----------------
df = pd.read_excel("Primary Analysis 042426.xlsx", sheet_name="Data")

# ---------------- CLEAN COLUMNS ----------------
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

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

# ---------- ACCOUNT ----------
if "Account_name" in df.columns:
    account = st.sidebar.multiselect(
        "Account",
        options=df["Account_name"].dropna().unique(),
        default=df["Account_name"].dropna().unique()
    )
else:
    account = []

# ---------- DOCTOR ----------
if "Doctor" in df.columns:
    doctor = st.sidebar.multiselect(
        "Doctor",
        options=df["Doctor"].dropna().unique(),
        default=df["Doctor"].dropna().unique()
    )
else:
    doctor = []

# ---------- USER ----------
if "Responsible_User_Name" in df.columns:
    user = st.sidebar.multiselect(
        "User",
        options=df["Responsible_User_Name"].dropna().unique(),
        default=df["Responsible_User_Name"].dropna().unique()
    )
else:
    user = []

# ---------- T/F FILTER ----------
if tf_col:
    tf_filter = st.sidebar.multiselect(
        "T/F",
        options=df[tf_col].dropna().unique(),
        default=df[tf_col].dropna().unique()
    )
else:
    tf_filter = []

# ---------------- APPLY FILTERS ----------------
filtered_df = df.copy()

if account:
    filtered_df = filtered_df[filtered_df["Account_name"].isin(account)]

if doctor:
    filtered_df = filtered_df[filtered_df["Doctor"].isin(doctor)]

if user:
    filtered_df = filtered_df[filtered_df["Responsible_User_Name"].isin(user)]

if tf_col and tf_filter:
    filtered_df = filtered_df[filtered_df[tf_col].isin(tf_filter)]

# ---------------- KPI LOGIC ----------------
final_df = filtered_df.copy()

df_false = final_df.copy()

total_audited_files = df_false["File_name"].nunique() if "File_name" in df_false.columns else 0

go_files = df_false[
    df_false["NoGo/Go"] == "go"
]["File_name"].nunique() if "NoGo/Go" in df_false.columns else 0

nogo_files = df_false[
    df_false["NoGo/Go"] == "nogo"
]["File_name"].nunique() if "NoGo/Go" in df_false.columns else 0

go_percent = round((go_files / total_audited_files) * 100, 2) if total_audited_files else 0
nogo_percent = round((nogo_files / total_audited_files) * 100, 2) if total_audited_files else 0

# ---------------- KPI DISPLAY ----------------
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
