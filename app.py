import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="CQA Go / NoGo Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# COLOR SYSTEM (one palette, used everywhere)
# =====================================================
COLORS = {
    "go": "#22c55e",        # green
    "nogo": "#ef4444",      # red
    "primary": "#2563eb",   # blue - accents / trend lines
    "muted": "#64748b",     # slate - secondary text
    "bg_card": "#ffffff",
    "bg_app": "#f5f7fa",
    "border": "#e5e7eb",
}
GO_NOGO_MAP = {"go": COLORS["go"], "nogo": COLORS["nogo"]}
SEQ_SCALE = ["#dbeafe", "#93c5fd", "#3b82f6", "#1d4ed8", "#1e3a8a"]  # single blue scale, used for all ranked bars

CHART_TEMPLATE = "plotly_white"
FONT = dict(family="Segoe UI, Helvetica, Arial, sans-serif", size=13, color="#1f2937")

# =====================================================
# GLOBAL CSS
# =====================================================
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {COLORS['bg_app']}; }}

    /* KPI cards */
    .kpi-card {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        text-align: left;
    }}
    .kpi-label {{
        font-size: 13px;
        color: {COLORS['muted']};
        font-weight: 600;
        letter-spacing: .02em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 30px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }}
    .kpi-sub {{
        font-size: 12px;
        color: {COLORS['muted']};
        margin-top: 4px;
    }}

    /* Section headers */
    .section-title {{
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0 2px 0;
    }}
    .section-sub {{
        font-size: 13px;
        color: {COLORS['muted']};
        margin-bottom: 10px;
    }}

    div[data-testid="stExpander"], .stTabs {{
        background-color: {COLORS['bg_card']};
        border-radius: 12px;
    }}
    h1 {{ font-weight: 800 !important; color: #0f172a !important; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* Tighter dataframe look */
    div[data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# HEADER
# =====================================================
st.markdown(
    """
    <div style="padding:6px 0 18px 0;">
        <div style="font-size:30px;font-weight:800;color:#0f172a;">📊 CQA Go / NoGo Dashboard</div>
        <div style="font-size:14px;color:#64748b;">Quality audit performance at a glance — filter, drill down, and export.</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_excel("Primary Analysis 042426.xlsx", sheet_name="Data")

    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", "", regex=True)
        .str.replace("\r", "", regex=True)
        .str.replace("\t", "", regex=True)
        .str.strip()
    )

    tf_col = None
    for col in df.columns:
        if "t/f" in col.lower().replace(" ", ""):
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


def download_csv(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8")


def style_fig(fig, height=380):
    """Apply one consistent look to every chart."""
    fig.update_layout(
        template=CHART_TEMPLATE,
        font=FONT,
        title_font=dict(size=16, color="#0f172a"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None),
        height=height,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eef1f5")
    return fig


def make_pivot(dataframe, index_col):
    pivot = dataframe.pivot_table(
        index=index_col, columns="NoGo/Go", values="Account_name", aggfunc="count", fill_value=0
    ).reset_index()
    pivot.columns.name = None
    if "go" not in pivot.columns:
        pivot["go"] = 0
    if "nogo" not in pivot.columns:
        pivot["nogo"] = 0
    pivot.rename(columns={index_col: index_col, "go": "Go", "nogo": "NoGo"}, inplace=True)
    pivot["Total"] = pivot["Go"] + pivot["NoGo"]
    pivot["NoGo %"] = ((pivot["NoGo"] / pivot["Total"]) * 100).round(2)
    return pivot.sort_values("NoGo %", ascending=False)


# =====================================================
# SIDEBAR — FILTERS
# =====================================================
st.sidebar.markdown("### 🔍 Filters")
st.sidebar.caption("Narrow down the data shown across the whole dashboard.")

date_filter = st.sidebar.multiselect("Date", sorted(df["Audited Date"].dropna().unique()))
account_filter = st.sidebar.multiselect("Account", sorted(df["Account_name"].dropna().unique()))
doctor_filter = st.sidebar.multiselect("Doctor", sorted(df["Doctor"].dropna().unique()))
user_filter = st.sidebar.multiselect("User", sorted(df["Responsible_User_Name"].dropna().unique()))
status_filter = st.sidebar.multiselect("Responsible User Status", sorted(df["Responsible_User_Status"].dropna().unique()))
initial_filter = st.sidebar.multiselect("Initial", sorted(df["Initial"].dropna().unique()))
tf_filter = st.sidebar.multiselect("T/F", sorted(df[tf_col].dropna().unique()), default=["false"])

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit · CQA Go / NoGo Dashboard")

filtered_df = df.copy()
if date_filter:
    filtered_df = filtered_df[filtered_df["Audited Date"].isin(date_filter)]
if account_filter:
    filtered_df = filtered_df[filtered_df["Account_name"].isin(account_filter)]
if doctor_filter:
    filtered_df = filtered_df[filtered_df["Doctor"].isin(doctor_filter)]
if user_filter:
    filtered_df = filtered_df[filtered_df["Responsible_User_Name"].isin(user_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df["Responsible_User_Status"].isin(status_filter)]
if initial_filter:
    filtered_df = filtered_df[filtered_df["Initial"].isin(initial_filter)]
if tf_filter:
    filtered_df = filtered_df[filtered_df[tf_col].isin(tf_filter)]

# =====================================================
# KPI SUMMARY
# =====================================================
total_files = len(filtered_df)
go_files = len(filtered_df[filtered_df["NoGo/Go"] == "go"])
nogo_files = len(filtered_df[filtered_df["NoGo/Go"] == "nogo"])
go_percent = round((go_files / total_files) * 100, 1) if total_files else 0
nogo_percent = round((nogo_files / total_files) * 100, 1) if total_files else 0

kpis = [
    ("📄 Total Files", f"{total_files:,}", "All audited records in view"),
    ("✅ Go", f"{go_files:,}", f"{go_percent}% of total"),
    ("❌ NoGo", f"{nogo_files:,}", f"{nogo_percent}% of total"),
    ("👤 Active Users", f"{filtered_df['Responsible_User_Name'].nunique():,}", "Responsible users in view"),
    ("🩺 Doctors Covered", f"{filtered_df['Doctor'].nunique():,}", "Unique doctors audited"),
]

st.markdown('<div class="section-title">📌 Key Metrics</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Snapshot of the currently filtered data.</div>', unsafe_allow_html=True)

kpi_cols = st.columns(len(kpis))
for col, (label, value, sub) in zip(kpi_cols, kpis):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")
st.download_button("⬇️ Download Filtered Raw Data", download_csv(filtered_df), "Filtered_Data.csv", "text/csv")

# =====================================================
# GO / NOGO SPLIT + DAILY TREND
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">📈 Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Overall pass rate and how volume moves day to day.</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns([1, 1.4], gap="large")

with chart_col1:
    fig = go.Figure(data=[go.Pie(
        labels=["Go", "NoGo"],
        values=[go_files, nogo_files],
        hole=0.65,
        marker=dict(colors=[COLORS["go"], COLORS["nogo"]]),
        textinfo="percent",
        textfont=dict(size=14, color="white"),
    )])
    fig.update_layout(
        title="Go vs NoGo Distribution",
        annotations=[dict(text=f"{go_percent}%<br><span style='font-size:11px;color:#64748b'>Go rate</span>",
                           x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    st.plotly_chart(style_fig(fig, height=360), use_container_width=True)

with chart_col2:
    if "Audited Date" in filtered_df.columns and len(filtered_df):
        trend = filtered_df.groupby("Audited Date").size().reset_index(name="Files").sort_values("Audited Date")
        fig = px.area(
            trend, x="Audited Date", y="Files", markers=True, title="Daily Audit Volume"
        )
        fig.update_traces(line_color=COLORS["primary"], fillcolor="rgba(37,99,235,0.12)",
                           marker=dict(size=7, color=COLORS["primary"]))
        fig.update_xaxes(type="category", tickangle=45, title_text="")
        st.plotly_chart(style_fig(fig, height=360), use_container_width=True)

# =====================================================
# BREAKDOWNS — USER / INITIAL / DOCTOR
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">🔎 Breakdowns</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Drill into performance by user, initial, or doctor.</div>', unsafe_allow_html=True)

user_pivot = make_pivot(filtered_df, "Responsible_User_Name").rename(columns={"Responsible_User_Name": "User"})
initial_pivot = make_pivot(filtered_df, "Initial")
doctor_pivot = make_pivot(filtered_df, "Doctor")

tab1, tab2, tab3 = st.tabs(["👤 User Wise", "🏥 Initial Wise", "🩺 Doctor Wise"])

with tab1:
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.dataframe(user_pivot, hide_index=True, use_container_width=True)
    with c2:
        fig = px.bar(user_pivot.sort_values("NoGo", ascending=False).head(10),
                     x="User", y="NoGo", color="NoGo", text="NoGo",
                     title="Top 10 Users by NoGo Count", color_continuous_scale=SEQ_SCALE)
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

with tab2:
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.dataframe(initial_pivot, hide_index=True, use_container_width=True)
    with c2:
        fig = px.bar(initial_pivot, x="Initial", y="NoGo %", color="NoGo %", text="NoGo %",
                     title="NoGo % by Initial", color_continuous_scale=SEQ_SCALE)
        fig.update_traces(textposition="outside", texttemplate="%{text}%")
        st.plotly_chart(style_fig(fig), use_container_width=True)

with tab3:
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.dataframe(doctor_pivot, hide_index=True, use_container_width=True)
    with c2:
        fig = px.bar(doctor_pivot.sort_values("NoGo", ascending=False).head(10),
                     x="Doctor", y="NoGo", color="NoGo", text="NoGo",
                     title="Top 10 Doctors by NoGo Count", color_continuous_scale=SEQ_SCALE)
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

# =====================================================
# PERFORMANCE SUMMARY
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">🏆 Performance Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Best and worst performing users, side by side.</div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    st.markdown("**🥇 Top 10 Best Performers**")
    if len(user_pivot):
        best_users = user_pivot[user_pivot["Total"] > 0].sort_values(["Go", "NoGo %"], ascending=[False, True]).head(10)
        st.dataframe(best_users, hide_index=True, use_container_width=True)
        fig = px.bar(best_users, x="User", y="Go", text="Go", title="Top 10 Users by Go Files")
        fig.update_traces(marker_color=COLORS["go"], textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

with right:
    st.markdown("**🚨 Top 10 Needs Attention**")
    if len(user_pivot):
        worst_users = user_pivot[user_pivot["Total"] > 0].sort_values(["NoGo", "NoGo %"], ascending=[False, False]).head(10)
        st.dataframe(worst_users, hide_index=True, use_container_width=True)
        fig = px.bar(worst_users, x="User", y="NoGo", text="NoGo", title="Top 10 Users by NoGo Files")
        fig.update_traces(marker_color=COLORS["nogo"], textposition="outside")
        st.plotly_chart(style_fig(fig), use_container_width=True)

# =====================================================
# MONTHLY TREND
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">📅 Monthly Trend</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Go vs NoGo volume across months.</div>', unsafe_allow_html=True)

if "Audited Date" in filtered_df.columns and len(filtered_df):
    trend_df = filtered_df.copy()
    trend_df["Month"] = pd.to_datetime(trend_df["Audited Date"]).dt.to_period("M").astype(str)
    monthly = trend_df.groupby(["Month", "NoGo/Go"]).size().reset_index(name="Files")

    fig = px.bar(
        monthly, x="Month", y="Files", color="NoGo/Go", barmode="group", text="Files",
        title="Monthly Go / NoGo Trend", color_discrete_map=GO_NOGO_MAP
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(type="category", title_text="")
    st.plotly_chart(style_fig(fig, height=420), use_container_width=True)

# =====================================================
# USER GO / NOGO STACKED BREAKDOWN
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">📊 Go vs NoGo by User</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Full breakdown of every user in the current filter.</div>', unsafe_allow_html=True)

stack_df = user_pivot.copy()
chart = stack_df.melt(id_vars="User", value_vars=["Go", "NoGo"], var_name="Status", value_name="Files")

fig = px.bar(
    chart, x="User", y="Files", color="Status", barmode="stack", text="Files",
    title="User Wise Go / NoGo Breakdown", color_discrete_map=GO_NOGO_MAP
)
fig.update_traces(textposition="inside")
fig.update_xaxes(title_text="")
st.plotly_chart(style_fig(fig, height=440), use_container_width=True)

# =====================================================
# DOWNLOADS
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">⬇️ Export Pivot Tables</div>', unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)
with d1:
    st.download_button("Download User Pivot", user_pivot.to_csv(index=False), "User_Pivot.csv", "text/csv")
with d2:
    st.download_button("Download Initial Pivot", initial_pivot.to_csv(index=False), "Initial_Pivot.csv", "text/csv")
with d3:
    st.download_button("Download Doctor Pivot", doctor_pivot.to_csv(index=False), "Doctor_Pivot.csv", "text/csv")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Developed using Streamlit · CQA Go / NoGo Dashboard · Version 2.0")
