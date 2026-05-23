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
    df[tf_col] = (
        df[tf_col]
        .astype(str)
        .str.strip()
        .str.lower()
    )

if "NoGo/Go" in df.columns:
    df["NoGo/Go"] = (
        df["NoGo/Go"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

# ================= FILTERS =================
st.sidebar.header("🔍 Filters")

account = st.sidebar.multiselect(
    "Account",
    options=sorted(df["Account_name"].dropna().unique())
    if "Account_name" in df.columns else [],
    default=[]
)

doctor = st.sidebar.multiselect(
    "Doctor",
    options=sorted(df["Doctor"].dropna().unique())
    if "Doctor" in df.columns else [],
    default=[]
)

user = st.sidebar.multiselect(
    "User",
    options=sorted(df["Responsible_User_Name"].dropna().unique())
    if "Responsible_User_Name" in df.columns else [],
    default=[]
)

status_filter = st.sidebar.multiselect(
    "Responsible User Status",
    options=sorted(df["Responsible_User_Status"].dropna().unique())
    if "Responsible_User_Status" in df.columns else [],
    default=[]
)

initial_filter = st.sidebar.multiselect(
    "Initial",
    options=sorted(df["Initial"].dropna().unique())
    if "Initial" in df.columns else [],
    default=[]
)

tf_filter = st.sidebar.multiselect(
    "T/F",
    options=sorted(df[tf_col].dropna().unique())
    if tf_col else [],
    default=["false"] if tf_col else []
)

# ================= APPLY FILTERS =================
filtered_df = df.copy()

if account:
    filtered_df = filtered_df[
        filtered_df["Account_name"].isin(account)
    ]

if doctor:
    filtered_df = filtered_df[
        filtered_df["Doctor"].isin(doctor)
    ]

if user:
    filtered_df = filtered_df[
        filtered_df["Responsible_User_Name"].isin(user)
    ]

if status_filter:
    filtered_df = filtered_df[
        filtered_df["Responsible_User_Status"].isin(status_filter)
    ]

if initial_filter:
    filtered_df = filtered_df[
        filtered_df["Initial"].isin(initial_filter)
    ]

if tf_col and tf_filter:
    filtered_df = filtered_df[
        filtered_df[tf_col].isin(tf_filter)
    ]

# ================= KPI DATA =================
kpi_df = filtered_df.copy()

# ---------------- KPI CALCULATION ----------------
total_audited_files = len(kpi_df)

go_files = len(
    kpi_df[kpi_df["NoGo/Go"] == "go"]
) if "NoGo/Go" in kpi_df.columns else 0

nogo_files = len(
    kpi_df[kpi_df["NoGo/Go"] == "nogo"]
) if "NoGo/Go" in kpi_df.columns else 0

go_percent = round(
    (go_files / total_audited_files) * 100,
    2
) if total_audited_files else 0

nogo_percent = round(
    (nogo_files / total_audited_files) * 100,
    2
) if total_audited_files else 0

# ================= KPI UI =================
st.subheader("📌 KPI Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Audited Files", total_audited_files)
col2.metric("Go Files", go_files)
col3.metric("Go %", f"{go_percent}%")
col4.metric("NoGo Files", nogo_files)
col5.metric("NoGo %", f"{nogo_percent}%")

# ================= USER WISE PIVOT =================

st.subheader("📋 User Wise Quality Summary")

if (
    "Responsible_User_Name" in filtered_df.columns
    and "NoGo/Go" in filtered_df.columns
):

    # ---------------- CREATE PIVOT ----------------
    pivot_df = pd.pivot_table(
        filtered_df,
        index="Responsible_User_Name",
        columns="NoGo/Go",
        values="Account_name",
        aggfunc="count",
        fill_value=0
    ).reset_index()

    pivot_df.columns.name = None

    # ---------------- HANDLE MISSING COLUMNS ----------------
    if "go" not in pivot_df.columns:
        pivot_df["go"] = 0

    if "nogo" not in pivot_df.columns:
        pivot_df["nogo"] = 0

    # ---------------- RENAME ----------------
    pivot_df = pivot_df.rename(columns={
        "Responsible_User_Name": "User Name",
        "go": "Go",
        "nogo": "NoGo"
    })

    # ---------------- CALCULATIONS ----------------
    pivot_df["Grand Total"] = (
        pivot_df["Go"] + pivot_df["NoGo"]
    )

    pivot_df["NoGo%"] = (
        (pivot_df["NoGo"] / pivot_df["Grand Total"]) * 100
    ).round(2)

    # ---------------- SORT ----------------
    pivot_df = pivot_df.sort_values(
        by="NoGo",
        ascending=False
    )

    # ================= GRAND TOTAL =================

    total_go = pivot_df["Go"].sum()

    total_nogo = pivot_df["NoGo"].sum()

    total_grand = pivot_df["Grand Total"].sum()

    total_nogo_percent = round(
        (total_nogo / total_grand) * 100,
        2
    ) if total_grand else 0

    grand_total_row = pd.DataFrame([{
        "User Name": "Grand Total",
        "Go": total_go,
        "NoGo": total_nogo,
        "Grand Total": total_grand,
        "NoGo%": total_nogo_percent
    }])

    pivot_df = pd.concat(
        [pivot_df, grand_total_row],
        ignore_index=True
    )

    # ---------------- FORMAT % ----------------
    pivot_df["NoGo%"] = (
        pivot_df["NoGo%"]
        .astype(str) + "%"
    )

    # ================= DISPLAY TABLE =================

    st.dataframe(
        pivot_df,
        hide_index=True,
        height=400,
        use_container_width=False
    )
