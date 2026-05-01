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

if tf_col:
    df[tf_col] = df[tf_col].astype(str).str.strip().str.lower()

if "NoGo/Go" in df.columns:
    df["NoGo/Go"] = df["NoGo/Go"].astype(str).str.strip().str.lower()

# ================= FILTERS =================
st.sidebar.header("🔍 Filters")

account = st.sidebar.multiselect(
    "Account",
    options=df["Account_name"].dropna().unique() if "Account_name" in df.columns else [],
    default=[]
)

doctor = st.sidebar.multiselect(
    "Doctor",
    options=df["Doctor"].dropna().unique() if "Doctor" in df.columns else [],
    default=[]
)

user = st.sidebar.multiselect(
    "User",
    options=df["Responsible_User_Name"].dropna().unique() if "Responsible_User_Name" in df.columns else [],
    default=[]
)

tf_filter = st.sidebar.multiselect(
    "T/F",
    options=df[tf_col].dropna().unique() if tf_col else [],
    default=[]
)

# ================= APPLY FILTERS =================
filtered_df = df.copy()

if account:
    filtered_df = filtered_df[filtered_df["Account_name"].isin(account)]

if doctor:
    filtered_df = filtered_df[filtered_df["Doctor"].isin(doctor)]

if user:
    filtered_df = filtered_df[filtered_df["Responsible_User_Name"].isin(user)]

if tf_col and tf_filter:
    filtered_df = filtered_df[filtered_df[tf_col].isin(tf_filter)]

# ================= 💥 IMPORTANT FIX =================
# REMOVE DUPLICATE FILES (THIS IS YOUR MAIN ISSUE FIX)

unique_df = filtered_df.drop_duplicates(subset=["File_name"])

# ================= KPI LOGIC =================
total_audited_files = unique_df["File_name"].nunique() if "File_name" in unique_df.columns else 0

go_files = unique_df[unique_df["NoGo/Go"] == "go"]["File_name"].nunique() if "NoGo/Go" in unique_df.columns else 0

nogo_files = unique_df[unique_df["NoGo/Go"] == "nogo"]["File_name"].nunique() if "NoGo/Go" in unique_df.columns else 0

go_percent = round((go_files / total_audited_files) * 100, 2) if total_audited_files else 0
nogo_percent = round((nogo_files / total_audited_files) * 100, 2) if total_audited_files else 0

# ================= UI =================
st.subheader("📌 KPI Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Audited Files", total_audited_files)
col2.metric("Go Files", go_files)
col3.metric("Go %", go_percent)
col4.metric("NoGo Files", nogo_files)
col5.metric("NoGo %", nogo_percent)

# ================= TABLE =================
st.subheader("📄 Detailed Data Table")
st.dataframe(unique_df, use_container_width=True)

# ================= CHARTS =================
st.subheader("📊 Analysis")

if "Doctor" in unique_df.columns:
    st.bar_chart(unique_df["Doctor"].value_counts())

if "Account_name" in unique_df.columns:
    st.bar_chart(unique_df["Account_name"].value_counts())

if "Responsible_User_Name" in unique_df.columns:
    st.bar_chart(unique_df["Responsible_User_Name"].value_counts())
