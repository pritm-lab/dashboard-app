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

if tf_col:
    df[tf_col] = df[tf_col].astype(str).str.strip().str.lower()

if "NoGo/Go" in df.columns:
    df["NoGo/Go"] = df["NoGo/Go"].astype(str).str.strip().str.lower()

# ================= FILTERS =================
st.sidebar.header("🔍 Filters")

account = st.sidebar.multiselect("Account", df["Account_name"].dropna().unique() if "Account_name" in df.columns else [])
doctor = st.sidebar.multiselect("Doctor", df["Doctor"].dropna().unique() if "Doctor" in df.columns else [])
user = st.sidebar.multiselect("User", df["Responsible_User_Name"].dropna().unique() if "Responsible_User_Name" in df.columns else [])

# ================= APPLY FILTERS =================
filtered_df = df.copy()

if account:
    filtered_df = filtered_df[filtered_df["Account_name"].isin(account)]
if doctor:
    filtered_df = filtered_df[filtered_df["Doctor"].isin(doctor)]
if user:
    filtered_df = filtered_df[filtered_df["Responsible_User_Name"].isin(user)]

# ================= KPI =================
total = len(filtered_df)
go = len(filtered_df[filtered_df["NoGo/Go"] == "go"]) if "NoGo/Go" in filtered_df.columns else 0
nogo = len(filtered_df[filtered_df["NoGo/Go"] == "nogo"]) if "NoGo/Go" in filtered_df.columns else 0

st.subheader("📌 KPI Summary")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total", total)
c2.metric("Go", go)
c3.metric("Go %", f"{round(go/total*100,2) if total else 0}%")
c4.metric("NoGo", nogo)
c5.metric("NoGo %", f"{round(nogo/total*100,2) if total else 0}%")

# ================= SAFE PIVOT FUNCTION =================
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

    # % numeric
    pivot["NoGo%"] = (pivot["NoGo"] / pivot["Total"] * 100).round(2)

    # ---------------- SPLIT DATA ----------------
    grand = pivot[pivot[label] == "Grand Total"].copy()
    pivot = pivot[pivot[label] != "Grand Total"]

    # ---------------- SORT ONLY MAIN DATA ----------------
    pivot = pivot.sort_values("NoGo", ascending=False)

    # ---------------- RE-ATTACH GRAND TOTAL ----------------
    grand = pd.DataFrame([{
        label: "Grand Total",
        "Go": pivot["Go"].sum(),
        "NoGo": pivot["NoGo"].sum(),
        "Total": pivot["Total"].sum(),
        "NoGo%": round((pivot["NoGo"].sum() / pivot["Total"].sum()) * 100, 2)
        if pivot["Total"].sum() else 0
    }])

    final_df = pd.concat([pivot, grand], ignore_index=True)

    final_df["NoGo%"] = final_df["NoGo%"].astype(str) + "%"

    return final_df[[label, "Go", "NoGo", "Total", "NoGo%"]]

# ================= 3 PIVOTS =================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👤 User Wise")
    st.dataframe(make_pivot(filtered_df, "Responsible_User_Name", "User"),
                 height=350, use_container_width=True)

with col2:
    st.subheader("🏥 Initial Wise")
    st.dataframe(make_pivot(filtered_df, "Initial", "Initial"),
                 height=350, use_container_width=True)

with col3:
    st.subheader("🩺 Doctor Wise")
    st.dataframe(make_pivot(filtered_df, "Doctor", "Doctor"),
                 height=350, use_container_width=True)
