import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# =====================================================
# PAGE CONFIG & EXACT MOCKUP VISUAL THEMING
# =====================================================
st.set_page_config(
    page_title="MIS Dashboard",
    page_icon="📊",
    layout="wide"
)

# Deep styling to copy the exact card layout, gray canvas, borders, fonts, and drop shadows
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Background Page Setup */
    .stApp {
        background-color: #ebedf2 !important;
    }
    
    /* Clean CSS Card implementation matching the uploaded mockup */
    .mockup-card {
        background-color: #ffffff !important;
        border: 1px solid #dcdfe6 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 24px !important;
    }
    
    div[data-testid="stMetricContainer"] {
        background-color: #ffffff !important;
        border: 1px solid #e4e7ed !important;
        padding: 20px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    }
    
    /* Sidebar matching design aesthetics */
    section[data-testid="stSidebar"] {
        background-color: #f4f6f9 !important;
        border-right: 1px solid #dcdfe6 !important;
    }
    
    h1, h2, h3, h4, p, span, div {
        font-family: 'Inter', sans-serif !important;
    }
    
    h1 {
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    
    /* Standardized padding override */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 CQA Go / NoGo Dashboard")
st.markdown("<p style='color: #64748b; font-size: 15px; margin-top: -10px;'>Interactive dashboard for Go / NoGo Quality Analysis.</p>", unsafe_allow_html=True)

# =====================================================
# CACHE DATA LOAD
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_excel("Primary Analysis 042426.xlsx", sheet_name="Data")
    df.columns = df.columns.astype(str).str.replace("\n","").str.replace("\r","").str.replace("\t","").str.strip()
    
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
# SIDEBAR FILTERS
# =====================================================
st.sidebar.markdown("<h3 style='margin-bottom:15px;'>🔍 Filters</h3>", unsafe_allow_html=True)
date_filter = st.sidebar.multiselect("Date", sorted(df["Audited Date"].dropna().unique()))
account_filter = st.sidebar.multiselect("Account", sorted(df["Account_name"].dropna().unique()))
doctor_filter = st.sidebar.multiselect("Doctor", sorted(df["Doctor"].dropna().unique()))
user_filter = st.sidebar.multiselect("User", sorted(df["Responsible_User_Name"].dropna().unique()))
status_filter = st.sidebar.multiselect("Responsible User Status", sorted(df["Responsible_User_Status"].dropna().unique()))
initial_filter = st.sidebar.multiselect("Initial", sorted(df["Initial"].dropna().unique()))
tf_filter = st.sidebar.multiselect("T/F", sorted(df[tf_col].dropna().unique()), default=["false"])

# Filter Execution
filtered_df = df.copy()
if date_filter: filtered_df = filtered_df[filtered_df["Audited Date"].isin(date_filter)]
if account_filter: filtered_df = filtered_df[filtered_df["Account_name"].isin(account_filter)]
if doctor_filter: filtered_df = filtered_df[filtered_df["Doctor"].isin(doctor_filter)]
if user_filter: filtered_df = filtered_df[filtered_df["Responsible_User_Name"].isin(user_filter)]
if status_filter: filtered_df = filtered_df[filtered_df["Responsible_User_Status"].isin(status_filter)]
if initial_filter: filtered_df = filtered_df[filtered_df["Initial"].isin(initial_filter)]
if tf_filter: filtered_df = filtered_df[filtered_df[tf_col].isin(tf_filter)]

# Calculations
total_files = len(filtered_df)
go_files = len(filtered_df[filtered_df["NoGo/Go"] == "go"])
nogo_files = len(filtered_df[filtered_df["NoGo/Go"] == "nogo"])
go_percent = round((go_files / total_files) * 100, 1) if total_files else 0
nogo_percent = round((nogo_files / total_files) * 100, 1) if total_files else 0

# =====================================================
# KPI SUMMARY SECTION
# =====================================================
st.markdown("<h3 style='margin-top:20px; color:#1e293b;'>📌 KPI Summary</h3>", unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📄 Total Files", total_files)
k2.metric("✅ Go", go_files)
k3.metric("🟢 Go %", f"{go_percent}%")
k4.metric("❌ NoGo", nogo_files)
k5.metric("🔴 NoGo %", f"{nogo_percent}%")

# =====================================================
# OVERVIEW COUNTS
# =====================================================
st.markdown("<h3 style='margin-top:25px; color:#1e293b;'>📋 Dashboard Overview</h3>", unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
s1.metric("👤 Unique Users", filtered_df["Responsible_User_Name"].nunique())
s2.metric("🏥 Unique Initials", filtered_df["Initial"].nunique())
s3.metric("🩺 Unique Doctors", filtered_df["Doctor"].nunique())
s4.metric("🏢 Unique Accounts", filtered_df["Account_name"].nunique())

# Helper formatting function for layout cards
def wrap_in_card(element_id):
    pass

# =====================================================
# THE FIRST TWO CORE VISUAL CORES
# =====================================================
st.markdown("<br>", unsafe_allow_html=True)
c_left, c_right = st.columns(2)

with c_left:
    st.markdown('<div class="mockup-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-bottom:-10px; color:#1e293b;'>Go vs NoGo Distribution</h4>", unsafe_allow_html=True)
    fig_pie = px.pie(
        names=["Go", "NoGo"], values=[go_files, nogo_files], hole=.55,
        color_discrete_sequence=["#2ecc71", "#e74c3c"]
    )
    fig_pie.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=0.9, xanchor="right", x=1)
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_right:
    st.markdown('<div class="mockup-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-bottom:-10px; color:#1e293b;'>Daily Audit Trend</h4>", unsafe_allow_html=True)
    if "Audited Date" in filtered_df.columns:
        trend = filtered_df.groupby("Audited Date").size().reset_index(name="Files").sort_values("Audited Date")
        fig_trend = px.line(trend, x="Audited Date", y="Files", markers=True, text="Files")
        fig_trend.update_traces(
            line=dict(color="#2980b9", width=2),
            marker=dict(size=8, color="#1abc9c", symbol="circle"),
            textposition="top center"
        )
        fig_trend.update_layout(
            plot_bgcolor="rgba(255,255,255,1)", paper_bgcolor="rgba(255,255,255,1)",
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(type='category', showgrid=False, tickangle=0)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Process Pivot Matrices
user_pivot = filtered_df.pivot_table(index="Responsible_User_Name", columns="NoGo/Go", values="Account_name", aggfunc="count", fill_value=0).reset_index()
if "go" not in user_pivot.columns: user_pivot["go"] = 0
if "nogo" not in user_pivot.columns: user_pivot["nogo"] = 0
user_pivot.rename(columns={"Responsible_User_Name": "User", "go": "Go", "nogo": "NoGo"}, inplace=True)
user_pivot["Total"] = user_pivot["Go"] + user_pivot["NoGo"]
user_pivot["NoGo %"] = ((user_pivot["NoGo"] / user_pivot["Total"]) * 100).round(2)
user_pivot = user_pivot.sort_values("NoGo %", ascending=False)

# =====================================================
# PERFORMANCE SUMMARY PLOT MATRIX 
# =====================================================
st.markdown('<div class="mockup-card">', unsafe_allow_html=True)
st.markdown("<h2 style='color:#1e293b; margin-bottom: 20px;'>🏆 Performance Summary</h2>", unsafe_allow_html=True)
p_left, p_right = st.columns(2)

with p_left:
    st.markdown("<h4 style='color:#2ecc71;'>🥇 Top 10 Best Performers</h4>", unsafe_allow_html=True)
    best_users = user_pivot[user_pivot["Total"] > 0].sort_values(["Go", "NoGo %"], ascending=[False, True]).head(10)
    st.dataframe(best_users, hide_index=True, use_container_width=True)
    
    # Matching precise custom color maps from image models
    fig_best = px.bar(best_users, x="User", y="Go", text="Go", color="Go", color_continuous_scale="Viridis")
    fig_best.update_layout(plot_bgcolor="rgba(255,255,255,1)", paper_bgcolor="rgba(255,255,255,1)", coloraxis_showscale=False)
    fig_best.update_traces(textposition="outside")
    st.plotly_chart(fig_best, use_container_width=True)

with p_right:
    st.markdown("<h4 style='color:#e74c3c;'>🚨 Top 10 Worst Performers</h4>", unsafe_allow_html=True)
    worst_users = user_pivot[user_pivot["Total"] > 0].sort_values(["NoGo", "NoGo %"], ascending=[False, False]).head(10)
    st.dataframe(worst_users, hide_index=True, use_container_width=True)
    
    fig_worst = px.bar(worst_users, x="User", y="NoGo", text="NoGo", color="NoGo", color_continuous_scale="Reds")
    fig_worst.update_layout(plot_bgcolor="rgba(255,255,255,1)", paper_bgcolor="rgba(255,255,255,1)", coloraxis_showscale=False)
    fig_worst.update_traces(textposition="outside")
    st.plotly_chart(fig_worst, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# MONTHLY TREND BLOCK
# =====================================================
if "Audited Date" in filtered_df.columns:
    st.markdown('<div class="mockup-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#1e293b;'>📈 Monthly Trend</h3>", unsafe_allow_html=True)
    trend_df = filtered_df.copy()
    trend_df["Month"] = pd.to_datetime(trend_df["Audited Date"]).dt.to_period("M").astype(str)
    monthly = trend_df.groupby(["Month", "NoGo/Go"]).size().reset_index(name="Files")
    
    fig_mon = px.bar(monthly, x="Month", y="Files", color="NoGo/Go", barmode="group", text="Files", color_discrete_map={"go": "#2ecc71", "nogo": "#e74c3c"})
    fig_mon.update_traces(textposition="outside")
    fig_mon.update_layout(plot_bgcolor="rgba(255,255,255,1)", paper_bgcolor="rgba(255,255,255,1)", xaxis=dict(type='category'))
    st.plotly_chart(fig_mon, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# USER BREAKDOWN REPLICA PLOT
# =====================================================
st.markdown('<div class="mockup-card">', unsafe_allow_html=True)
st.markdown("<h3 style='color:#1e293b;'>📊 Go vs NoGo By User</h3>", unsafe_allow_html=True)
chart_stack = user_pivot.copy().melt(id_vars="User", value_vars=["Go", "NoGo"], var_name="Status", value_name="Files")
fig_stack = px.bar(chart_stack, x="User", y="Files", color="Status", barmode="stack", text="Files", color_discrete_map={"Go": "#2ecc71", "NoGo": "#e74c3c"})
fig_stack.update_traces(textposition="inside")
fig_stack.update_layout(plot_bgcolor="rgba(255,255,255,1)", paper_bgcolor="rgba(255,255,255,1)")
st.plotly_chart(fig_stack, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Download buttons
st.markdown("<br>", unsafe_allow_html=True)
st.download_button("⬇ Download Filtered Raw Data", download_csv(filtered_df), "Filtered_Data.csv", "text/csv")
