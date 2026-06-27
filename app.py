import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =====================================================
# PAGE CONFIG & PREMIUM CUSTOM STYLING (The Mockup Look)
# =====================================================
st.set_page_config(
    page_title="MIS Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS injection to create a matching gray container backdrop with soft shadows
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background-color: #f1f3f6 !important;
    }
    
    /* Global Card/Container styling */
    div[data-testid="stVerticalBlock"] > div[class*="element-container"] {
        background-color: transparent;
    }
    
    /* Metrics blocks container styling */
    div[data-testid="stMetricContainer"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Make custom container sections look wrapped */
    .plot-container {
        background-color: #ffffff !important;
        padding: 15px !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #e2e8f0 !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 CQA Go / NoGo Dashboard")
st.markdown("Interactive dashboard for Go / NoGo Quality Analysis.")

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
        df[tf_col] = df[tf_col].astype(str).str.strip().str.lower()
    if "NoGo/Go" in df.columns:
        df["NoGo/Go"] = df["NoGo/Go"].astype(str).str.strip().str.lower()
    if "Audited Date" in df.columns:
        df["Audited Date"] = pd.to_datetime(df["Audited Date"]).dt.date
    return df, tf_col

df, tf_col = load_data()

# =====================================================
# DOWNLOAD FUNCTION
# =====================================================
def download_csv(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8")

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("🔍 Filters")
date_filter = st.sidebar.multiselect("Date", sorted(df["Audited Date"].dropna().unique()))
account_filter = st.sidebar.multiselect("Account", sorted(df["Account_name"].dropna().unique()))
doctor_filter = st.sidebar.multiselect("Doctor", sorted(df["Doctor"].dropna().unique()))
user_filter = st.sidebar.multiselect("User", sorted(df["Responsible_User_Name"].dropna().unique()))
status_filter = st.sidebar.multiselect("Responsible User Status", sorted(df["Responsible_User_Status"].dropna().unique()))
initial_filter = st.sidebar.multiselect("Initial", sorted(df["Initial"].dropna().unique()))
tf_filter = st.sidebar.multiselect("T/F", sorted(df[tf_col].dropna().unique()), default=["false"])

# Filter Logic
filtered_df = df.copy()
if date_filter: filtered_df = filtered_df[filtered_df["Audited Date"].isin(date_filter)]
if account_filter: filtered_df = filtered_df[filtered_df["Account_name"].isin(account_filter)]
if doctor_filter: filtered_df = filtered_df[filtered_df["Doctor"].isin(doctor_filter)]
if user_filter: filtered_df = filtered_df[filtered_df["Responsible_User_Name"].isin(user_filter)]
if status_filter: filtered_df = filtered_df[filtered_df["Responsible_User_Status"].isin(status_filter)]
if initial_filter: filtered_df = filtered_df[filtered_df["Initial"].isin(initial_filter)]
if tf_filter: filtered_df = filtered_df[filtered_df[tf_col].isin(tf_filter)]

# =====================================================
# KPI SUMMARY
# =====================================================
total_files = len(filtered_df)
go_files = len(filtered_df[filtered_df["NoGo/Go"] == "go"])
nogo_files = len(filtered_df[filtered_df["NoGo/Go"] == "nogo"])
go_percent = round((go_files / total_files) * 100, 2) if total_files else 0
nogo_percent = round((nogo_files / total_files) * 100, 2) if total_files else 0

st.subheader("📌 KPI Summary")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📄 Total Files", total_files)
k2.metric("✅ Go", go_files)
k3.metric("🟢 Go %", f"{go_percent}%")
k4.metric("❌ NoGo", nogo_files)
k5.metric("🔴 NoGo %", f"{nogo_percent}%")

# =====================================================
# DASHBOARD OVERVIEW (Position 2)
# =====================================================
st.markdown("---")
st.subheader("📋 Dashboard Overview")
s1, s2, s3, s4 = st.columns(4)
s1.metric("👤 Unique Users", filtered_df["Responsible_User_Name"].nunique())
s2.metric("🏥 Unique Initials", filtered_df["Initial"].nunique())
s3.metric("🩺 Unique Doctors", filtered_df["Doctor"].nunique())
s4.metric("🏢 Unique Accounts", filtered_df["Account_name"].nunique())

st.download_button("⬇ Download Filtered Raw Data", download_csv(filtered_df), "Filtered_Data.csv", "text/csv")

# =====================================================
# PLOTLY CHART THEME COMPONENT SETUP
# =====================================================
def apply_premium_layout(fig):
    fig.update_layout(
        plot_bgcolor="rgba(248,250,252,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        font=dict(family="Inter, sans-serif", size=12, color="#334155"),
        margin=dict(l=40, r=40, t=50, b=40),
        showlegend=True
    )
    fig.update_xaxes(showgrid=False, linecolor="#cbd5e1")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0", linecolor="#cbd5e1")
    return fig

# =====================================================
# DISTRIBUTION & DAILY TREND CHARTS
# =====================================================
st.markdown("---")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_pie = px.pie(
        names=["Go", "NoGo"], values=[go_files, nogo_files], hole=.55,
        title="Go vs NoGo Distribution", color_discrete_sequence=["#2ecc71", "#e74c3c"]
    )
    fig_pie.update_layout(paper_bgcolor="rgba(255,255,255,1)")
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    if "Audited Date" in filtered_df.columns:
        trend = filtered_df.groupby("Audited Date").size().reset_index(name="Files").sort_values("Audited Date")
        fig_trend = px.line(trend, x="Audited Date", y="Files", markers=True, text="Files", title="Daily Audit Trend")
        fig_trend.update_traces(line_color="#2980b9", marker=dict(size=10, color="#16a085"), textposition="top center")
        fig_trend.update_xaxes(type='category', tickangle=45)
        fig_trend = apply_premium_layout(fig_trend)
        st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# DATA TABS
# =====================================================
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["👤 User Wise", "🏥 Initial Wise", "🩺 Doctor Wise"])

# Setup generic pivot processes
user_pivot = filtered_df.pivot_table(index="Responsible_User_Name", columns="NoGo/Go", values="Account_name", aggfunc="count", fill_value=0).reset_index()
if "go" not in user_pivot.columns: user_pivot["go"] = 0
if "nogo" not in user_pivot.columns: user_pivot["nogo"] = 0
user_pivot.rename(columns={"Responsible_User_Name": "User", "go": "Go", "nogo": "NoGo"}, inplace=True)
user_pivot["Total"] = user_pivot["Go"] + user_pivot["NoGo"]
user_pivot["NoGo %"] = ((user_pivot["NoGo"] / user_pivot["Total"]) * 100).round(2)
user_pivot = user_pivot.sort_values("NoGo %", ascending=False)

with tab1:
    c1, c2 = st.columns([3, 2])
    c1.dataframe(user_pivot, hide_index=True, use_container_width=True)
    fig_u = px.bar(user_pivot.head(10), x="User", y="NoGo", color="NoGo", text="NoGo", title="Top 10 NoGo Users", color_continuous_scale="Reds")
    fig_u = apply_premium_layout(fig_u)
    c2.plotly_chart(fig_u, use_container_width=True)

# =====================================================
# PERFORMANCE SUMMARY (Custom Styled Gradient Bars)
# =====================================================
st.markdown("---")
st.header("🏆 Performance Summary")
left, right = st.columns(2)

with left:
    st.subheader("🥇 Top 10 Best Performers")
    best_users = user_pivot[user_pivot["Total"] > 0].sort_values(["Go", "NoGo %"], ascending=[False, True]).head(10)
    st.dataframe(best_users, hide_index=True, use_container_width=True)
    fig_best = px.bar(best_users, x="User", y="Go", color="Go", text="Go", title="Top 10 Users by Go Files", color_continuous_scale="Viridis")
    fig_best = apply_premium_layout(fig_best)
    st.plotly_chart(fig_best, use_container_width=True)

with right:
    st.subheader("🚨 Top 10 Worst Performers")
    worst_users = user_pivot[user_pivot["Total"] > 0].sort_values(["NoGo", "NoGo %"], ascending=[False, False]).head(10)
    st.dataframe(worst_users, hide_index=True, use_container_width=True)
    fig_worst = px.bar(worst_users, x="User", y="NoGo", color="NoGo", text="NoGo", title="Top 10 Users by NoGo Files", color_continuous_scale="Reds")
    fig_worst = apply_premium_layout(fig_worst)
    st.plotly_chart(fig_worst, use_container_width=True)

# =====================================================
# MONTHLY TREND WITH LABELS OUTSIDE
# =====================================================
st.markdown("---")
st.header("📈 Monthly Trend")
if "Audited Date" in filtered_df.columns:
    trend_df = filtered_df.copy()
    trend_df["Month"] = pd.to_datetime(trend_df["Audited Date"]).dt.to_period("M").astype(str)
    monthly = trend_df.groupby(["Month", "NoGo/Go"]).size().reset_index(name="Files")
    
    fig_mon = px.bar(monthly, x="Month", y="Files", color="NoGo/Go", barmode="group", text="Files", title="Monthly Go / NoGo Trend", color_discrete_map={"go": "#2ecc71", "nogo": "#e74c3c"})
    fig_mon.update_traces(textposition="outside")
    fig_mon.update_xaxes(type='category')
    fig_mon = apply_premium_layout(fig_mon)
    st.plotly_chart(fig_mon, use_container_width=True)

# =====================================================
# USER GO / NOGO BREAKDOWN WITH STACKED INTERNAL LABELS
# =====================================================
st.markdown("---")
st.header("📊 Go vs NoGo By User")
chart_stack = user_pivot.copy().melt(id_vars="User", value_vars=["Go", "NoGo"], var_name="Status", value_name="Files")
fig_stack = px.bar(chart_stack, x="User", y="Files", color="Status", barmode="stack", text="Files", title="User Wise Go / NoGo Breakdown", color_discrete_map={"Go": "#2ecc71", "NoGo": "#e74c3c"})
fig_stack.update_traces(textposition="inside")
fig_stack = apply_premium_layout(fig_stack)
st.plotly_chart(fig_stack, use_container_width=True)

# Downloads
st.markdown("---")
st.subheader("⬇ Pivot Table Downloads")
d1, d2, d3 = st.columns(3)
d1.download_button("Download User Pivot", user_pivot.to_csv(index=False), "User_Pivot.csv", "text/csv")

st.markdown("---")
st.caption("Developed using Streamlit | CQA Go / NoGo Dashboard | Version 1.3")
