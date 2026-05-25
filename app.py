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

# ================= DATE FIX =================
if "Audited Date" in df.columns:
    df["Audited Date"] = pd.to_datetime(df["Audited Date"], errors="coerce").dt.date

# ================= FILTERS =================
st.sidebar.header("🔍 Filters")

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
    filtered_df = filtered_df[filtered_df["Audited Date"].isin(Date)]

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
total_audited_files = len(filtered_df)

go_files = len(filtered_df[filtered_df["NoGo/Go"] == "go"]) if "NoGo/Go" in filtered_df.columns else 0
nogo_files = len(filtered_df[filtered_df["NoGo/Go"] == "nogo"]) if "NoGo/Go" in filtered_df.columns else 0

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

# ================= FUNCTION (NO MISTAKE ZONE) =================
def build_pivot(df, idx_col):

    if idx_col not in df.columns:
        return None

    pivot = pd.pivot_table(
        df,
        index=idx_col,
        columns="NoGo/Go",
        values="Account_name",
        aggfunc="count",
        fill_value=0
    ).reset_index()

    pivot.columns.name = None

    pivot["go"] = pivot.get("go", 0)
    pivot["nogo"] = pivot.get("nogo", 0)

    pivot = pivot.rename(columns={
        idx_col: "Name",
        "go": "Go",
        "nogo": "NoGo"
    })

    pivot["Total"] = pivot["Go"] + pivot["NoGo"]

    # 🔥 IMPORTANT FIX (proper decimal + sorting safe)
    pivot["NoGo%_num"] = (
        pivot["NoGo"] / pivot["Total"].replace(0, 1) * 100
    )

    pivot["NoGo%"] = pivot["NoGo%_num"].map("{:.2f}%")

    pivot = pivot.sort_values(by="NoGo%_num", ascending=False)

    return pivot


# ================= USER =================
with col1:
    st.subheader("👤 User Wise")
    user_pivot = build_pivot(filtered_df, "Responsible_User_Name")
    if user_pivot is not None:
        st.dataframe(user_pivot, hide_index=True, use_container_width=True)

# ================= INITIAL =================
with col2:
    st.subheader("🏥 Initial Wise")
    initial_pivot = build_pivot(filtered_df, "Initial")
    if initial_pivot is not None:
        st.dataframe(initial_pivot, hide_index=True, use_container_width=True)

# ================= DOCTOR =================
with col3:
    st.subheader("🩺 Doctor Wise")
    doctor_pivot = build_pivot(filtered_df, "Doctor")
    if doctor_pivot is not None:
        st.dataframe(doctor_pivot, hide_index=True, use_container_width=True)
