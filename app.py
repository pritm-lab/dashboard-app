import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="MIS Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CQA Go / NoGo Dashboard")

st.markdown(
    """
    Interactive dashboard for Go / NoGo Quality Analysis.
    """
)

# =====================================================
# CACHE DATA
# =====================================================

@st.cache_data
def load_data():

    df = pd.read_excel(
        "Primary Analysis 042426.xlsx",
        sheet_name="Data"
    )

    df.columns = (
        df.columns.astype(str)
        .str.replace("\n","",regex=True)
        .str.replace("\r","",regex=True)
        .str.replace("\t","",regex=True)
        .str.strip()
    )

    tf_col = None

    for col in df.columns:

        if "t/f" in col.lower().replace(" ",""):
            tf_col = col
            break

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

    if "Audited Date" in df.columns:

        df["Audited Date"] = pd.to_datetime(
            df["Audited Date"]
        ).dt.date

    return df, tf_col


df, tf_col = load_data()

# =====================================================
# DOWNLOAD FUNCTION
# =====================================================

def download_csv(dataframe):

    return dataframe.to_csv(
        index=False
    ).encode("utf-8")


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("🔍 Filters")

date_filter = st.sidebar.multiselect(
    "Date",
    sorted(df["Audited Date"].dropna().unique())
)

account_filter = st.sidebar.multiselect(
    "Account",
    sorted(df["Account_name"].dropna().unique())
)

doctor_filter = st.sidebar.multiselect(
    "Doctor",
    sorted(df["Doctor"].dropna().unique())
)

user_filter = st.sidebar.multiselect(
    "User",
    sorted(df["Responsible_User_Name"].dropna().unique())
)

status_filter = st.sidebar.multiselect(
    "Responsible User Status",
    sorted(df["Responsible_User_Status"].dropna().unique())
)

initial_filter = st.sidebar.multiselect(
    "Initial",
    sorted(df["Initial"].dropna().unique())
)

tf_filter = st.sidebar.multiselect(
    "T/F",
    sorted(df[tf_col].dropna().unique()),
    default=["false"]
)

# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = df.copy()

if date_filter:

    filtered_df = filtered_df[
        filtered_df["Audited Date"].isin(date_filter)
    ]

if account_filter:

    filtered_df = filtered_df[
        filtered_df["Account_name"].isin(account_filter)
    ]

if doctor_filter:

    filtered_df = filtered_df[
        filtered_df["Doctor"].isin(doctor_filter)
    ]

if user_filter:

    filtered_df = filtered_df[
        filtered_df["Responsible_User_Name"].isin(user_filter)
    ]

if status_filter:

    filtered_df = filtered_df[
        filtered_df["Responsible_User_Status"].isin(status_filter)
    ]

if initial_filter:

    filtered_df = filtered_df[
        filtered_df["Initial"].isin(initial_filter)
    ]

if tf_filter:

    filtered_df = filtered_df[
        filtered_df[tf_col].isin(tf_filter)
    ]

# =====================================================
# KPI
# =====================================================

total_files = len(filtered_df)

go_files = len(
    filtered_df[
        filtered_df["NoGo/Go"]=="go"
    ]
)

nogo_files = len(
    filtered_df[
        filtered_df["NoGo/Go"]=="nogo"
    ]
)

go_percent = round(
    (go_files/total_files)*100,
    2
) if total_files else 0

nogo_percent = round(
    (nogo_files/total_files)*100,
    2
) if total_files else 0

st.subheader("📌 KPI Summary")

k1,k2,k3,k4,k5 = st.columns(5)

k1.metric(
    "📄 Total Files",
    total_files
)

k2.metric(
    "✅ Go",
    go_files
)

k3.metric(
    "🟢 Go %",
    f"{go_percent}%"
)

k4.metric(
    "❌ NoGo",
    nogo_files
)

k5.metric(
    "🔴 NoGo %",
    f"{nogo_percent}%"
)

# =====================================================
# DOWNLOAD BUTTON
# =====================================================

st.download_button(
    "⬇ Download Filtered Data",
    download_csv(filtered_df),
    "Filtered_Data.csv",
    "text/csv"
)

# =====================================================
# GO / NOGO CHART
# =====================================================

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    fig = px.pie(
        names=["Go","NoGo"],
        values=[go_files,nogo_files],
        hole=.55,
        title="Go vs NoGo"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with chart_col2:

    if "Audited Date" in filtered_df.columns:

        trend = (
            filtered_df
            .groupby("Audited Date")
            .size()
            .reset_index(name="Files")
        )

        fig = px.line(
            trend,
            x="Audited Date",
            y="Files",
            markers=True,
            title="Daily Audit Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# USER / INITIAL / DOCTOR ANALYSIS
# =====================================================

st.markdown("---")

tab1, tab2, tab3 = st.tabs(
    [
        "👤 User Wise",
        "🏥 Initial Wise",
        "🩺 Doctor Wise"
    ]
)

# =====================================================
# USER WISE
# =====================================================

with tab1:

    user_pivot = (
        filtered_df
        .pivot_table(
            index="Responsible_User_Name",
            columns="NoGo/Go",
            values="Account_name",
            aggfunc="count",
            fill_value=0
        )
        .reset_index()
    )

    user_pivot.columns.name = None

    if "go" not in user_pivot.columns:
        user_pivot["go"] = 0

    if "nogo" not in user_pivot.columns:
        user_pivot["nogo"] = 0

    user_pivot.rename(
        columns={
            "Responsible_User_Name":"User",
            "go":"Go",
            "nogo":"NoGo"
        },
        inplace=True
    )

    user_pivot["Total"] = (
        user_pivot["Go"] +
        user_pivot["NoGo"]
    )

    user_pivot["NoGo %"] = (
        (
            user_pivot["NoGo"] /
            user_pivot["Total"]
        )*100
    ).round(2)

    user_pivot = user_pivot.sort_values(
        "NoGo %",
        ascending=False
    )

    c1,c2 = st.columns([3,2])

    with c1:

        st.dataframe(
            user_pivot,
            hide_index=True,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            user_pivot.head(10),
            x="User",
            y="NoGo",
            color="NoGo",
            text="NoGo",
            title="Top 10 NoGo Users"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.download_button(
        "⬇ Download User Pivot",
        user_pivot.to_csv(index=False),
        "User_Pivot.csv",
        "text/csv"
    )

# =====================================================
# INITIAL WISE
# =====================================================

with tab2:

    initial_pivot = (
        filtered_df
        .pivot_table(
            index="Initial",
            columns="NoGo/Go",
            values="Account_name",
            aggfunc="count",
            fill_value=0
        )
        .reset_index()
    )

    initial_pivot.columns.name = None

    if "go" not in initial_pivot.columns:
        initial_pivot["go"] = 0

    if "nogo" not in initial_pivot.columns:
        initial_pivot["nogo"] = 0

    initial_pivot.rename(
        columns={
            "go":"Go",
            "nogo":"NoGo"
        },
        inplace=True
    )

    initial_pivot["Total"] = (
        initial_pivot["Go"] +
        initial_pivot["NoGo"]
    )

    initial_pivot["NoGo %"] = (
        (
            initial_pivot["NoGo"] /
            initial_pivot["Total"]
        )*100
    ).round(2)

    initial_pivot = initial_pivot.sort_values(
        "NoGo %",
        ascending=False
    )

    c1,c2 = st.columns([3,2])

    with c1:

        st.dataframe(
            initial_pivot,
            hide_index=True,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            initial_pivot,
            x="Initial",
            y="NoGo %",
            color="NoGo %",
            text="NoGo %",
            title="Initial Wise NoGo %"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.download_button(
        "⬇ Download Initial Pivot",
        initial_pivot.to_csv(index=False),
        "Initial_Pivot.csv",
        "text/csv"
    )

# =====================================================
# DOCTOR WISE
# =====================================================

with tab3:

    doctor_pivot = (
        filtered_df
        .pivot_table(
            index="Doctor",
            columns="NoGo/Go",
            values="Account_name",
            aggfunc="count",
            fill_value=0
        )
        .reset_index()
    )

    doctor_pivot.columns.name = None

    if "go" not in doctor_pivot.columns:
        doctor_pivot["go"] = 0

    if "nogo" not in doctor_pivot.columns:
        doctor_pivot["nogo"] = 0

    doctor_pivot.rename(
        columns={
            "go":"Go",
            "nogo":"NoGo"
        },
        inplace=True
    )

    doctor_pivot["Total"] = (
        doctor_pivot["Go"] +
        doctor_pivot["NoGo"]
    )

    doctor_pivot["NoGo %"] = (
        (
            doctor_pivot["NoGo"] /
            doctor_pivot["Total"]
        )*100
    ).round(2)

    doctor_pivot = doctor_pivot.sort_values(
        "NoGo %",
        ascending=False
    )

    c1,c2 = st.columns([3,2])

    with c1:

        st.dataframe(
            doctor_pivot,
            hide_index=True,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            doctor_pivot.head(10),
            x="Doctor",
            y="NoGo",
            color="NoGo",
            text="NoGo",
            title="Top 10 Doctors (NoGo)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.download_button(
        "⬇ Download Doctor Pivot",
        doctor_pivot.to_csv(index=False),
        "Doctor_Pivot.csv",
        "text/csv"
    )

# =====================================================
# PERFORMANCE SUMMARY
# =====================================================

st.markdown("---")
st.header("🏆 Performance Summary")

left, right = st.columns(2)

# =====================================================
# BEST PERFORMERS
# =====================================================

with left:

    st.subheader("🥇 Top 10 Best Performers")

    if len(user_pivot):

        best_users = (
            user_pivot[user_pivot["Total"] > 0]
            .sort_values(
                ["NoGo %", "Total"],
                ascending=[True, False]
            )
            .head(10)
        )

        st.dataframe(
            best_users,
            hide_index=True,
            use_container_width=True
        )

        fig = px.bar(
            best_users,
            x="User",
            y="NoGo %",
            color="NoGo %",
            text="NoGo %",
            title="Top 10 Best Users"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# WORST PERFORMERS
# =====================================================

with right:

    st.subheader("🚨 Top 10 Worst Performers")

    if len(user_pivot):

        worst_users = (
            user_pivot[user_pivot["Total"] > 0]
            .sort_values(
                ["NoGo %", "Total"],
                ascending=[False, False]
            )
            .head(10)
        )

        st.dataframe(
            worst_users,
            hide_index=True,
            use_container_width=True
        )

        fig = px.bar(
            worst_users,
            x="User",
            y="NoGo %",
            color="NoGo %",
            text="NoGo %",
            title="Top 10 Worst Users"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# MONTHLY TREND
# =====================================================

st.markdown("---")
st.header("📈 Monthly Trend")

if "Audited Date" in filtered_df.columns:

    trend_df = filtered_df.copy()

    trend_df["Month"] = pd.to_datetime(
        trend_df["Audited Date"]
    ).dt.to_period("M").astype(str)

    monthly = (
        trend_df
        .groupby(
            ["Month", "NoGo/Go"]
        )
        .size()
        .reset_index(name="Files")
    )

    fig = px.bar(
        monthly,
        x="Month",
        y="Files",
        color="NoGo/Go",
        barmode="group",
        title="Monthly Go / NoGo Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# USER GO / NOGO
# =====================================================

st.markdown("---")
st.header("📊 Go vs NoGo By User")

stack_df = user_pivot.copy()

chart = stack_df.melt(
    id_vars="User",
    value_vars=["Go", "NoGo"],
    var_name="Status",
    value_name="Files"
)

fig = px.bar(
    chart,
    x="User",
    y="Files",
    color="Status",
    barmode="stack",
    title="User Wise Go / NoGo"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# OVERALL SUMMARY
# =====================================================

st.markdown("---")
st.header("📋 Dashboard Summary")

s1, s2, s3, s4 = st.columns(4)

s1.metric(
    "👤 Users",
    filtered_df["Responsible_User_Name"].nunique()
)

s2.metric(
    "🏥 Initials",
    filtered_df["Initial"].nunique()
)

s3.metric(
    "🩺 Doctors",
    filtered_df["Doctor"].nunique()
)

s4.metric(
    "🏢 Accounts",
    filtered_df["Account_name"].nunique()
)

# =====================================================
# DOWNLOAD ALL PIVOTS
# =====================================================

st.markdown("---")
st.subheader("⬇ Downloads")

d1, d2, d3 = st.columns(3)

with d1:

    st.download_button(
        "Download User Pivot",
        user_pivot.to_csv(index=False),
        "User_Pivot.csv",
        "text/csv"
    )

with d2:

    st.download_button(
        "Download Initial Pivot",
        initial_pivot.to_csv(index=False),
        "Initial_Pivot.csv",
        "text/csv"
    )

with d3:

    st.download_button(
        "Download Doctor Pivot",
        doctor_pivot.to_csv(index=False),
        "Doctor_Pivot.csv",
        "text/csv"
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "Developed using Streamlit | CQA Go / NoGo Dashboard | Version 1.0"
)
