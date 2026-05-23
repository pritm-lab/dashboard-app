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

account = st.sidebar.multiselect(
    "Account",
    df["Account_name"].dropna().unique() if "Account_name" in df.columns else []
)

doctor = st.sidebar.multiselect(
    "Doctor",
    df["Doctor"].dropna().unique() if "Doctor" in df.columns else []
)

user = st.sidebar.multiselect(
    "User",
    df["Responsible_User_Name"].dropna().unique() if "Responsible_User_Name" in df.columns else []
)

status_filter = st.sidebar.multiselect(
    "Responsible User Status",
    df["Responsible_User_Status"].dropna().unique() if "Responsible_User_Status" in df.columns else []
)

initial_filter = st.sidebar.multiselect(
    "Initial",
    df["Initial"].dropna().unique() if "Initial" in df.columns else []
)

tf_filter = st.sidebar.multiselect(
    "T/F",
    df[tf_col].dropna().unique() if tf_col else [],
    default=["false"] if tf_col else []
)

# ================= APPLY FILTERS =================
filtered_df = df.copy()

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

total = len(kpi_df)
go = len(kpi_df[kpi_df["NoGo/Go"] == "go"]) if "NoGo/Go" in kpi_df.columns else 0
nogo = len(kpi_df[kpi_df["NoGo/Go"] == "nogo"]) if "NoGo/Go" in kpi_df.columns else 0

go_pct = round((go / total) * 100, 2) if total else 0
nogo_pct = round((nogo / total) * 100, 2) if total else 0

st.subheader("📌 KPI Summary")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total", total)
c2.metric("Go", go)
c3.metric("Go %", f"{go_pct}%")
c4.metric("NoGo", nogo)
c5.metric("NoGo %", f"{nogo_pct}%")

# ================= FUNCTION (COMMON PIVOT) =================
def make_pivot(data, index_col, label):

    pivot = pd.pivot_table(
        data,
        index=index_col,
        columns="NoGo/Go",
        values="Account_name",
        aggfunc="count",
        fill_value=0
    ).reset_index()

    pivot.columns.name = None

    pivot = pivot.rename(columns={
        index_col: label,
        "go": "Go",
        "nogo": "NoGo"
    })

    pivot["Go"] = pivot.get("Go", 0)
    pivot["NoGo"] = pivot.get("NoGo", 0)

    pivot["Total"] = pivot["Go"] + pivot["NoGo"]

    # keep numeric (IMPORTANT for sorting)
    pivot["NoGo%_num"] = (pivot["NoGo"] / pivot["Total"] * 100).round(2)

    # GRAND TOTAL ROW (NO SORT TOUCH)
    grand = pd.DataFrame([{
        label: "Grand Total",
        "Go": pivot["Go"].sum(),
        "NoGo": pivot["NoGo"].sum(),
        "Total": pivot["Total"].sum(),
        "NoGo%_num": round(
            (pivot["NoGo"].sum() / pivot["Total"].sum()) * 100, 2
        ) if pivot["Total"].sum() else 0
    }])

    pivot = pivot[pivot[label] != "Grand Total"]

    # sort ONLY real data
    pivot = pivot.sort_values("NoGo", ascending=False)

    # attach grand total at bottom (FREEZE FIX)
    pivot = pd.concat([pivot, grand], ignore_index=True)

    # final display column (after sorting)
    pivot["NoGo%"] = pivot["NoGo%_num"].astype(str) + "%"

    return pivot[[label, "Go", "NoGo", "Total", "NoGo%"]]

# ================= 3 PIVOTS =================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👤 User Wise")
    if "Responsible_User_Name" in filtered_df.columns:
        st.dataframe(
            make_pivot(filtered_df, "Responsible_User_Name", "User"),
            height=350,
            use_container_width=True
        )

with col2:
    st.subheader("🏥 Initial Wise")
    if "Initial" in filtered_df.columns:
        st.dataframe(
            make_pivot(filtered_df, "Initial", "Initial"),
            height=350,
            use_container_width=True
        )

with col3:
    st.subheader("🩺 Doctor Wise")
    if "Doctor" in filtered_df.columns:
        st.dataframe(
            make_pivot(filtered_df, "Doctor", "Doctor"),
            height=350,
            use_container_width=True
        )
