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

# ================= HELPER FUNCTION =================
def build_pivot(df, index_col):
    pivot = pd.pivot_table(
        df,
        index=index_col,
        columns="NoGo/Go",
        values="Account_name",
        aggfunc="count",
        fill_value=0
    ).reset_index()

    pivot.columns.name = None

    pivot = pivot.rename(columns={
        "go": "Go",
        "nogo": "NoGo",
        index_col: index_col
    })

    pivot["Go"] = pivot.get("Go", 0)
    pivot["NoGo"] = pivot.get("NoGo", 0)

    pivot["Total"] = pivot["Go"] + pivot["NoGo"]

    pivot["NoGo%"] = pivot.apply(
        lambda x: round((x["NoGo"] / x["Total"]) * 100, 2) if x["Total"] else 0,
        axis=1
    )

    return pivot

# ================= 3 PIVOTS =================
col1, col2, col3 = st.columns(3)

# ---------------- USER ----------------
with col1:
    st.subheader("👤 User Wise")

    if "Responsible_User_Name" in filtered_df.columns:

        user_pivot = build_pivot(filtered_df, "Responsible_User_Name")
        user_pivot = user_pivot.rename(columns={"Responsible_User_Name": "User"})

        # Grand Total (NO SORT ISSUE)
        gt = pd.DataFrame([{
            "User": "Grand Total",
            "Go": user_pivot["Go"].sum(),
            "NoGo": user_pivot["NoGo"].sum(),
            "Total": user_pivot["Total"].sum(),
            "NoGo%": round((user_pivot["NoGo"].sum() / user_pivot["Total"].sum()) * 100, 2)
        }])

        user_pivot = pd.concat([user_pivot, gt], ignore_index=True)
        user_pivot["NoGo%"] = user_pivot["NoGo%"].astype(str) + "%"

        st.dataframe(user_pivot, height=350, use_container_width=True)

# ---------------- INITIAL ----------------
with col2:
    st.subheader("🏥 Initial Wise")

    if "Initial" in filtered_df.columns:

        initial_pivot = build_pivot(filtered_df, "Initial")

        gt = pd.DataFrame([{
            "Initial": "Grand Total",
            "Go": initial_pivot["Go"].sum(),
            "NoGo": initial_pivot["NoGo"].sum(),
            "Total": initial_pivot["Total"].sum(),
            "NoGo%": round((initial_pivot["NoGo"].sum() / initial_pivot["Total"].sum()) * 100, 2)
        }])

        initial_pivot = pd.concat([initial_pivot, gt], ignore_index=True)
        initial_pivot["NoGo%"] = initial_pivot["NoGo%"].astype(str) + "%"

        st.dataframe(initial_pivot, height=350, use_container_width=True)

# ---------------- DOCTOR ----------------
with col3:
    st.subheader("🩺 Doctor Wise")

    if "Doctor" in filtered_df.columns:

        doctor_pivot = build_pivot(filtered_df, "Doctor")

        gt = pd.DataFrame([{
            "Doctor": "Grand Total",
            "Go": doctor_pivot["Go"].sum(),
            "NoGo": doctor_pivot["NoGo"].sum(),
            "Total": doctor_pivot["Total"].sum(),
            "NoGo%": round((doctor_pivot["NoGo"].sum() / doctor_pivot["Total"].sum()) * 100, 2)
        }])

        doctor_pivot = pd.concat([doctor_pivot, gt], ignore_index=True)
        doctor_pivot["NoGo%"] = doctor_pivot["NoGo%"].astype(str) + "%"

        st.dataframe(doctor_pivot, height=350, use_container_width=True)
