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
# HOSPITAL / PHYSICIAN DEEP-DIVE
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">🏥 Hospital & Physician Deep-dive</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Go/NoGo and quality performance sliced by subhospital, physician, and location.</div>', unsafe_allow_html=True)


def make_quality_pivot(dataframe, index_col):
    """Same as make_pivot, plus average Accuracy / Overall Score where those columns exist."""
    if index_col not in dataframe.columns:
        return pd.DataFrame()
    base = make_pivot(dataframe, index_col)
    for extra_col, label in [("Accuracy", "Avg Accuracy"), ("Overall Score", "Avg Overall Score")]:
        if extra_col in dataframe.columns:
            avg = (
                dataframe.assign(_num=pd.to_numeric(dataframe[extra_col], errors="coerce"))
                .groupby(index_col)["_num"].mean().round(2)
            )
            base = base.merge(avg.rename(label), on=index_col, how="left")
    return base


hosp_tab, doc_tab, loc_tab = st.tabs(["🏨 Subhospital", "🩺 Physician", "📍 Location"])

with hosp_tab:
    if "Subhospital" in filtered_df.columns:
        hosp_pivot = make_quality_pivot(filtered_df, "Subhospital")
        c1, c2 = st.columns([3, 2], gap="medium")
        with c1:
            st.dataframe(hosp_pivot, hide_index=True, use_container_width=True)
        with c2:
            fig = px.bar(
                hosp_pivot.sort_values("NoGo %", ascending=False).head(10),
                x="Subhospital", y="NoGo %", text="NoGo %", title="Top 10 Subhospitals by NoGo %",
                color="NoGo %", color_continuous_scale=SEQ_SCALE
            )
            fig.update_traces(textposition="outside", texttemplate="%{text}%")
            fig.update_xaxes(title_text="")
            st.plotly_chart(style_fig(fig), use_container_width=True)
    else:
        st.info("Subhospital column not found in this data.")

with doc_tab:
    doc_quality_pivot = make_quality_pivot(filtered_df, "Doctor")
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        st.dataframe(doc_quality_pivot, hide_index=True, use_container_width=True)
    with c2:
        fig = px.bar(
            doc_quality_pivot.sort_values("NoGo %", ascending=False).head(10),
            x="Doctor", y="NoGo %", text="NoGo %", title="Top 10 Physicians by NoGo %",
            color="NoGo %", color_continuous_scale=SEQ_SCALE
        )
        fig.update_traces(textposition="outside", texttemplate="%{text}%")
        fig.update_xaxes(title_text="")
        st.plotly_chart(style_fig(fig), use_container_width=True)

with loc_tab:
    if "Location" in filtered_df.columns:
        loc_pivot = make_quality_pivot(filtered_df, "Location")
        c1, c2 = st.columns([3, 2], gap="medium")
        with c1:
            st.dataframe(loc_pivot, hide_index=True, use_container_width=True)
        with c2:
            fig = px.bar(
                loc_pivot.sort_values("Total", ascending=False).head(10),
                x="Location", y="Total", text="Total", title="Top 10 Locations by Volume",
                color="Total", color_continuous_scale=SEQ_SCALE
            )
            fig.update_traces(textposition="outside")
            fig.update_xaxes(title_text="")
            st.plotly_chart(style_fig(fig), use_container_width=True)
    else:
        st.info("Location column not found in this data.")

# =====================================================
# AUDITOR WORKLOAD & PRODUCTIVITY
# =====================================================
st.markdown("---")
st.markdown('<div class="section-title">👷 Auditor Workload &amp; Productivity</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Who is auditing how much, how fast, and status-wise split (e.g. MT / QA / BB).</div>', unsafe_allow_html=True)

if "Auditor_name" in filtered_df.columns and len(filtered_df):
    auditor_df = filtered_df.copy()
    auditor_df["_time_min"] = pd.to_numeric(auditor_df.get("Time_Taken_by_Auditor_in_mins"), errors="coerce")
    auditor_df["_screen_sec"] = pd.to_numeric(auditor_df.get("Auditor_Screen_Time_Spend_In_Seconds"), errors="coerce")

    auditor_summary = auditor_df.groupby("Auditor_name").agg(
        Files_Audited=("Auditor_name", "count"),
        Avg_Time_Taken_Min=("_time_min", "mean"),
        Total_Screen_Time_Hrs=("_screen_sec", lambda s: round(s.sum() / 3600, 1) if s.notna().any() else 0)
    ).reset_index()
    auditor_summary["Avg_Time_Taken_Min"] = auditor_summary["Avg_Time_Taken_Min"].round(1)
    auditor_summary = auditor_summary.sort_values("Files_Audited", ascending=False)

    avg_time_overall = round(auditor_df["_time_min"].mean(), 1) if auditor_df["_time_min"].notna().any() else "—"
    total_screen_hrs = round(auditor_df["_screen_sec"].sum() / 3600, 1) if auditor_df["_screen_sec"].notna().any() else "—"

    a1, a2, a3 = st.columns(3)
    for col, label, value in [
        (a1, "👷 Active Auditors", f"{auditor_df['Auditor_name'].nunique():,}"),
        (a2, "⏱ Avg Time / File (min)", avg_time_overall),
        (a3, "🖥 Total Screen Time (hrs)", total_screen_hrs),
    ]:
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True
        )

    st.write("")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig = px.bar(
            auditor_summary.head(15), x="Auditor_name", y="Files_Audited", text="Files_Audited",
            title="Files Audited per Auditor (Top 15)", color="Files_Audited", color_continuous_scale=SEQ_SCALE
        )
        fig.update_traces(textposition="outside")
        fig.update_xaxes(title_text="")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        fig = px.bar(
            auditor_summary.sort_values("Avg_Time_Taken_Min", ascending=False).head(15),
            x="Auditor_name", y="Avg_Time_Taken_Min", text="Avg_Time_Taken_Min",
            title="Avg Time Taken per File — Top 15 Slowest", color="Avg_Time_Taken_Min",
            color_continuous_scale=SEQ_SCALE
        )
        fig.update_traces(textposition="outside")
        fig.update_xaxes(title_text="")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    st.dataframe(auditor_summary, hide_index=True, use_container_width=True)

    if "Missed_Achieved" in filtered_df.columns:
        st.markdown("**🎯 Milestone: Achieved vs Missed (by Auditor)**")
        milestone = filtered_df.groupby(["Auditor_name", "Missed_Achieved"]).size().reset_index(name="Files")
        fig = px.bar(
            milestone, x="Auditor_name", y="Files", color="Missed_Achieved", barmode="stack",
            text="Files", title="Milestone Achieved vs Missed by Auditor"
        )
        fig.update_traces(textposition="inside")
        fig.update_xaxes(title_text="")
        st.plotly_chart(style_fig(fig, height=420), use_container_width=True)
else:
    st.info("Auditor_name column not found in this data.")

# --- Responsible User Status breakdown (e.g. MT / QA / BB) ---
if "Responsible_User_Status" in filtered_df.columns and len(filtered_df):
    st.markdown("**🏷️ Volume &amp; Quality by Responsible User Status (e.g. MT / QA / BB)**")
    status_pivot = make_pivot(filtered_df, "Responsible_User_Status")
    c1, c2 = st.columns([2, 3], gap="medium")
    with c1:
        st.dataframe(status_pivot, hide_index=True, use_container_width=True)
    with c2:
        status_chart = status_pivot.melt(
            id_vars="Responsible_User_Status", value_vars=["Go", "NoGo"], var_name="Status", value_name="Files"
        )
        fig = px.bar(
            status_chart, x="Responsible_User_Status", y="Files", color="Status", barmode="stack",
            text="Files", title="Go / NoGo by Responsible User Status", color_discrete_map=GO_NOGO_MAP
        )
        fig.update_traces(textposition="inside")
        fig.update_xaxes(title_text="")
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
