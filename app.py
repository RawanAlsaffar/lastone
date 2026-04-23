import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import warnings
import os
import json
warnings.filterwarnings('ignore')

# المسار الأساسي للمشروع (يعمل على أي جهاز)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
# إعدادات الصفحة
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="لوحة تحليل الكهرباء - الهلال الأحمر السعودي",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS الاحترافي - Dark Mode
# ─────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    direction: rtl;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-left: 1px solid #30363d;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #8b949e !important; font-size: 12px !important;
}
.sidebar-logo {
    text-align: center; padding: 20px 10px 10px;
    border-bottom: 1px solid #30363d; margin-bottom: 15px;
}
.sidebar-logo h2 { color: #e6edf3 !important; font-size: 16px !important; margin: 8px 0 2px !important; }
.sidebar-logo p { color: #8b949e !important; font-size: 11px !important; margin: 0 !important; }
.sidebar-crescent { font-size: 40px; line-height: 1; }
.kpi-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 18px 20px; position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); }
.kpi-card::before {
    content: ''; position: absolute; top: 0; right: 0;
    width: 4px; height: 100%; border-radius: 0 12px 12px 0;
}
.kpi-card.red::before { background: #c0392b; }
.kpi-card.green::before { background: #2ea043; }
.kpi-card.blue::before { background: #1f6feb; }
.kpi-card.orange::before { background: #d29922; }
.kpi-card.purple::before { background: #8957e5; }
.kpi-label { color: #8b949e; font-size: 12px; margin-bottom: 6px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #e6edf3; line-height: 1.2; }
.kpi-value.red { color: #f85149; }
.kpi-value.green { color: #3fb950; }
.kpi-value.blue { color: #58a6ff; }
.kpi-value.orange { color: #d29922; }
.kpi-value.purple { color: #bc8cff; }
.kpi-delta { font-size: 12px; margin-top: 4px; }
.kpi-delta.up { color: #3fb950; }
.kpi-delta.down { color: #f85149; }
.kpi-delta.neutral { color: #8b949e; }
.kpi-icon { position: absolute; top: 15px; left: 15px; font-size: 28px; opacity: 0.15; }
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin: 25px 0 15px; padding-bottom: 10px; border-bottom: 1px solid #21262d;
}
.section-header h3 { color: #e6edf3 !important; font-size: 16px !important; margin: 0 !important; }
.section-icon {
    background: #c0392b22; border-radius: 8px; padding: 6px 10px;
    font-size: 13px; color: #f85149; font-weight: 600; letter-spacing: 0.5px;
}
.main-header {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d; border-radius: 12px;
    padding: 20px 25px; margin-bottom: 20px;
    display: flex; justify-content: space-between; align-items: center;
}
.main-header h1 { color: #e6edf3 !important; font-size: 22px !important; margin: 0 !important; }
.main-header p { color: #8b949e !important; font-size: 13px !important; margin: 4px 0 0 !important; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-red { background: #c0392b22; color: #f85149; border: 1px solid #c0392b44; }
.badge-green { background: #2ea04322; color: #3fb950; border: 1px solid #2ea04344; }
.badge-blue { background: #1f6feb22; color: #58a6ff; border: 1px solid #1f6feb44; }
.badge-orange { background: #d2992222; color: #d29922; border: 1px solid #d2992244; }
.alert-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 12px 15px; margin: 6px 0;
}
.alert-card.warning { border-right: 3px solid #d29922; }
.alert-card.danger { border-right: 3px solid #f85149; }
.alert-card.info { border-right: 3px solid #58a6ff; }
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #161b22; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid #30363d;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent; color: #8b949e; border-radius: 8px;
    padding: 8px 16px; font-size: 13px; border: none;
}
[data-testid="stTabs"] [aria-selected="true"] { background: #c0392b !important; color: white !important; }
[data-baseweb="tag"] {
    background-color: #c0392b22 !important; border: 1px solid #c0392b44 !important; color: #f85149 !important;
}
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
hr { border-color: #21262d !important; }
[data-testid="stExpander"] {
    background: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px !important;
}
.stProgress > div > div > div { background: linear-gradient(90deg, #c0392b, #e74c3c) !important; }
[data-baseweb="select"] { background: #21262d !important; border-color: #30363d !important; }
[data-baseweb="select"] * { background: #21262d !important; color: #e6edf3 !important; }
[data-testid="stMetric"] {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 10px !important; padding: 12px !important;
}
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #e6edf3 !important; }
.quarter-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 15px; text-align: center; margin: 5px 0;
}
.quarter-card h4 { color: #8b949e !important; font-size: 12px !important; margin: 0 0 8px !important; }
.quarter-card .q-value { font-size: 20px; font-weight: 700; color: #e6edf3; }
.quarter-card .q-label { font-size: 11px; color: #8b949e; margin-top: 4px; }
.footer {
    text-align: center; color: #484f58; font-size: 11px;
    padding: 20px 0 10px; border-top: 1px solid #21262d; margin-top: 30px;
}
.stat-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 14px 16px; text-align: center;
}
.stat-card .stat-label { color: #8b949e; font-size: 11px; margin-bottom: 4px; }
.stat-card .stat-value { font-size: 20px; font-weight: 700; }
.stat-card .stat-year { font-size: 10px; color: #484f58; margin-top: 2px; }
.model-info-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 20px; margin-bottom: 15px;
}
.model-info-card h4 { color: #8b949e; font-size: 12px; margin: 0 0 8px; font-weight: 400; }
.model-info-card .model-value { font-size: 22px; font-weight: 700; line-height: 1.2; }
.model-info-card .model-sub { font-size: 11px; color: #484f58; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# تحميل البيانات
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    # نستخدم اسم الملف مباشرة لأنه في نفس المجلد على GitHub
    df = pd.read_csv('SRCA_Electricity_Data.csv') 
    df['Year'] = df['Year'].astype(int)
    df['Month'] = df['Month'].astype(int)
    df['Collective_CA'] = df['Collective_CA'].astype(str)
    df['Contract_Account'] = df['Contract_Account'].astype(str)
    return df

@st.cache_data
def load_predictions():
    return pd.read_csv('SRCA_2026_Predictions.csv')

@st.cache_data
def load_q1_comparison():
    return pd.read_csv('SRCA_Q1_2026_Comparison.csv')

@st.cache_data
def load_model_metrics():
    if os.path.exists('model_metrics.json'):
        with open('model_metrics.json', 'r') as f:
            return json.load(f)
    return None
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, 'SRCA_Electricity_Data.csv'))
    df['Year'] = df['Year'].astype(int)
    df['Month'] = df['Month'].astype(int)
    df['Collective_CA'] = df['Collective_CA'].astype(str)
    df['Contract_Account'] = df['Contract_Account'].astype(str)
    return df

@st.cache_data
def load_predictions():
    pred = pd.read_csv(os.path.join(BASE_DIR, 'SRCA_2026_Predictions.csv'))
    pred['Collective_CA'] = pred['Collective_CA'].astype(str)
    pred['Contract_Account'] = pred['Contract_Account'].astype(str)
    return pred

@st.cache_data
def load_q1_comparison():
    comp = pd.read_csv(os.path.join(BASE_DIR, 'SRCA_Q1_2026_Comparison.csv'))
    comp['Collective_CA'] = comp['Collective_CA'].astype(str)
    return comp

@st.cache_data
def load_model_metrics():
    metrics_path = os.path.join(BASE_DIR, 'model_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return None

df = load_data()
pred_df = load_predictions()
comp_df = load_q1_comparison()
model_metrics = load_model_metrics()

# ─────────────────────────────────────────────
# ثوابت
# ─────────────────────────────────────────────
MONTH_NAMES = {1:'يناير',2:'فبراير',3:'مارس',4:'أبريل',5:'مايو',6:'يونيو',
               7:'يوليو',8:'أغسطس',9:'سبتمبر',10:'أكتوبر',11:'نوفمبر',12:'ديسمبر'}
REGION_COLORS = {
    'الوسطى': '#e74c3c', 'الغربية': '#e67e22', 'الشرقية': '#f1c40f',
    'الجنوبية': '#2ecc71', 'الشمالية': '#3498db'
}
YEAR_COLORS = {2024: '#58a6ff', 2025: '#3fb950', 2026: '#f85149'}

# ─────────────────────────────────────────────
# دوال مساعدة Plotly
# ─────────────────────────────────────────────
def dark_layout(height=300, title='', showlegend=True, **extra):
    layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(22,27,34,0.8)',
        font=dict(color='#e6edf3', family='Arial'),
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        height=height,
        showlegend=showlegend,
    )
    if title:
        layout['title'] = dict(text=title, font=dict(color='#e6edf3', size=14))
    if showlegend:
        layout['legend'] = dict(
            bgcolor='rgba(22,27,34,0.9)', bordercolor='#30363d', borderwidth=1,
            font=dict(color='#e6edf3')
        )
    layout.update(extra)
    return layout

def dark_xaxis(**kwargs):
    base = dict(gridcolor='#21262d', linecolor='#30363d', tickfont=dict(color='#8b949e'))
    base.update(kwargs)
    return base

def dark_yaxis(**kwargs):
    base = dict(gridcolor='#21262d', linecolor='#30363d', tickfont=dict(color='#8b949e'))
    base.update(kwargs)
    return base

def fmt_num(n, unit=''):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M {unit}".strip()
    elif n >= 1_000:
        return f"{n/1_000:.1f}K {unit}".strip()
    return f"{n:.0f} {unit}".strip()

def delta_pct(new, old):
    if old == 0: return 0
    return ((new - old) / old) * 100

def sparkline_fig(values, color='#c0392b'):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    fill_color = f'rgba({r},{g},{b},0.15)'
    fig = go.Figure(go.Scatter(
        y=values, mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=fill_color
    ))
    fig.update_layout(
        height=50, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False
    )
    return fig

def kpi_card(label, value, delta=None, color='red', icon='', unit=''):
    delta_html = ''
    if delta is not None:
        arrow = '▲' if delta > 0 else '▼'
        cls = 'up' if delta > 0 else 'down'
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {abs(delta):.1f}% مقارنة بالعام السابق</div>'
    icon_html = f'<div class="kpi-icon">{icon}</div>' if icon else ''
    return f'<div class="kpi-card {color}">{icon_html}<div class="kpi-label">{label}</div><div class="kpi-value {color}">{value}</div>{delta_html}</div>'

# ─────────────────────────────────────────────
# الشريط الجانبي
# ─────────────────────────────────────────────
# ابحث عن هذا الجزء في كودك وعدله:
# ابحثي عن جزء اللوجو في Sidebar واستبدليه بهذا:
with st.sidebar:
    logo_path = 'SRCAlogo_local_cmyk.jpg' # اسم الملف مباشرة
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown('<h2 style="text-align:center;">🌙 الهلال الأحمر</h2>', unsafe_allow_html=True)

    st.markdown("### فلاتر البيانات")

    selected_years = st.multiselect(
        "السنة",
        options=[2024, 2025, 2026],
        default=[2024, 2025, 2026],
        key="years"
    )
    if not selected_years:
        selected_years = [2024, 2025, 2026]

    regions = ['الكل'] + sorted(df['Region_Major'].dropna().unique().tolist())
    selected_region = st.selectbox("المنطقة الرئيسية", regions, key="region")

    ca_options = ['الكل'] + sorted(df['Collective_CA'].unique().tolist())
    selected_ca = st.selectbox("الحساب التجميعي", ca_options, key="ca")

    max_cons = int(df['Consumption_kWh'].max())
    cons_range = st.slider("نطاق الاستهلاك (كيلوواط/ساعة)", 0, max_cons, (0, max_cons), key="cons")

    st.markdown("---")
    st.markdown(f"""
    <div style='text-align:center; color:#484f58; font-size:10px;'>
        الإصدار 2.0 | أبريل 2026<br>قسم تقنية المعلومات
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# تطبيق الفلاتر
# ─────────────────────────────────────────────
mask = df['Year'].isin(selected_years) & df['Consumption_kWh'].between(cons_range[0], cons_range[1])
if selected_region != 'الكل':
    mask &= df['Region_Major'] == selected_region
if selected_ca != 'الكل':
    mask &= df['Collective_CA'] == selected_ca

df_f = df[mask].copy()
df_24 = df_f[df_f['Year'] == 2024]
df_25 = df_f[df_f['Year'] == 2025]
df_26 = df_f[df_f['Year'] == 2026]

# ─────────────────────────────────────────────
# الرأس الرئيسي
# ─────────────────────────────────────────────
total_records = len(df_f)
st.markdown(f"""
<div class="main-header">
    <div>
        <h1>لوحة تحليل استهلاك الكهرباء</h1>
        <p>هيئة الهلال الأحمر السعودي | بيانات 2024 - 2026</p>
    </div>
    <div style="text-align:left;">
        <span class="badge badge-green">● مباشر</span>
        <div style="color:#8b949e; font-size:12px; margin-top:5px;">إجمالي السجلات: {total_records:,}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# التبويبات الرئيسية
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab_geo, tab4 = st.tabs([
    "نظرة عامة",
    "التحليل الإحصائي",
    "إدارة الأصول",
    "التحليل الجغرافي",
    "توقعات 2026"
])

# ══════════════════════════════════════════════
# تبويب 1: نظرة عامة
# ══════════════════════════════════════════════
with tab1:
    # KPI Cards
    total_24 = df_24['Consumption_kWh'].sum()
    total_25 = df_25['Consumption_kWh'].sum()
    total_26_actual = df_26['Consumption_kWh'].sum()
    total_pred_26 = pred_df[pred_df['Type'] == 'متوقع']['Predicted_Consumption'].sum()
    total_full_26 = pred_df['Predicted_Consumption'].sum()

    delta_25_24 = delta_pct(total_25, total_24)
    delta_26_25 = delta_pct(total_full_26, total_25)

    num_ca = df_f['Collective_CA'].nunique()
    num_sub = df_f['Contract_Account'].nunique()

    # صف KPIs الأول: الاستهلاك
    st.markdown('<div class="section-header"><span class="section-icon">kWh</span><h3>مؤشرات الاستهلاك (كيلوواط/ساعة)</h3></div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(kpi_card("إجمالي 2024", fmt_num(total_24), None, 'blue', '', 'كيلوواط'), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("إجمالي 2025", fmt_num(total_25), delta_25_24, 'green', '', 'كيلوواط'), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("توقعات 2026", fmt_num(total_full_26), delta_26_25, 'orange', '', 'كيلوواط'), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("الحسابات التجميعية", str(num_ca), None, 'purple', ''), unsafe_allow_html=True)
    with col5:
        st.markdown(kpi_card("الحسابات الفرعية", str(num_sub), None, 'red', ''), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # صف KPIs الثاني: التحليل المالي بالريال
    st.markdown('<div class="section-header"><span class="section-icon">SAR</span><h3>مؤشرات التحليل المالي (ريال سعودي)</h3></div>', unsafe_allow_html=True)

    bill_24 = df_24['Bill_Amount'].sum()
    bill_25 = df_25['Bill_Amount'].sum()
    bill_26 = df_26['Bill_Amount'].sum()
    delta_bill_25_24 = delta_pct(bill_25, bill_24)

    latest_yr = max(selected_years)
    num_ca_yr = df_f[df_f['Year'] == latest_yr]['Collective_CA'].nunique()
    num_sub_yr = df_f[df_f['Year'] == latest_yr]['Contract_Account'].nunique()

    fin_col1, fin_col2, fin_col3, fin_col4, fin_col5 = st.columns(5)
    with fin_col1:
        st.markdown(kpi_card("إجمالي الفواتير 2024", fmt_num(bill_24, 'SAR'), None, 'blue', ''), unsafe_allow_html=True)
    with fin_col2:
        st.markdown(kpi_card("إجمالي الفواتير 2025", fmt_num(bill_25, 'SAR'), delta_bill_25_24, 'green', ''), unsafe_allow_html=True)
    with fin_col3:
        st.markdown(kpi_card("فواتير 2026 (Q1)", fmt_num(bill_26, 'SAR'), None, 'orange', ''), unsafe_allow_html=True)
    with fin_col4:
        st.markdown(kpi_card(f"حسابات تجميعية ({latest_yr})", str(num_ca_yr), None, 'purple', ''), unsafe_allow_html=True)
    with fin_col5:
        st.markdown(kpi_card(f"حسابات تعاقدية ({latest_yr})", str(num_sub_yr), None, 'red', ''), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # صف KPIs الثالث: الإحصاءات الوصفية
    st.markdown('<div class="section-header"><span class="section-icon">إحصاء</span><h3>الإحصاءات الوصفية للاستهلاك (كيلوواط/ساعة)</h3></div>', unsafe_allow_html=True)

    stat_years = [2024, 2025, 2026]
    stat_labels = {2024: '2024', 2025: '2025', 2026: '2026 (Q1)'}
    stat_colors = {2024: '#58a6ff', 2025: '#3fb950', 2026: '#f85149'}

    stat_cols = st.columns(len(stat_years) * 4)
    col_idx = 0
    for yr in stat_years:
        d = df[df['Year'] == yr]['Consumption_kWh']
        mean_v = d.mean()
        median_v = d.median()
        std_v = d.std()
        color = stat_colors[yr]
        label = stat_labels[yr]

        with stat_cols[col_idx]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">المتوسط</div>
                <div class="stat-value" style="color:{color};">{fmt_num(mean_v)}</div>
                <div class="stat-year">{label}</div>
            </div>
            """, unsafe_allow_html=True)
        col_idx += 1

        with stat_cols[col_idx]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">الوسيط</div>
                <div class="stat-value" style="color:{color};">{fmt_num(median_v)}</div>
                <div class="stat-year">{label}</div>
            </div>
            """, unsafe_allow_html=True)
        col_idx += 1

        with stat_cols[col_idx]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">الانحراف المعياري</div>
                <div class="stat-value" style="color:{color};">{fmt_num(std_v)}</div>
                <div class="stat-year">{label}</div>
            </div>
            """, unsafe_allow_html=True)
        col_idx += 1

        if yr == 2025:
            d_24 = df[df['Year'] == 2024]['Consumption_kWh']
            mean_24 = d_24.mean()
            change_pct = delta_pct(mean_v, mean_24)
            arrow = '▲' if change_pct > 0 else '▼'
            chg_color = '#3fb950' if change_pct > 0 else '#f85149'
            with stat_cols[col_idx]:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">معدل التغير 24 - 25</div>
                    <div class="stat-value" style="color:{chg_color};">{arrow} {abs(change_pct):.1f}%</div>
                    <div class="stat-year">نسبة مئوية</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with stat_cols[col_idx]:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">عدد السجلات</div>
                    <div class="stat-value" style="color:{color};">{len(d):,}</div>
                    <div class="stat-year">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        col_idx += 1

    st.markdown("<br>", unsafe_allow_html=True)

    # الرسوم البيانية الرئيسية
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-header"><span class="section-icon">بياني</span><h3>الاتجاه الشهري للاستهلاك</h3></div>', unsafe_allow_html=True)

        trend = df_f[df_f['Year'].isin([2024, 2025, 2026])].groupby(['Year', 'Month'])['Consumption_kWh'].sum().reset_index()

        fig_trend = go.Figure()
        dash_map = {2024: 'dot', 2025: 'solid', 2026: 'dash'}
        for yr in sorted(trend['Year'].unique()):
            d = trend[trend['Year'] == yr].sort_values('Month')
            fig_trend.add_trace(go.Scatter(
                x=d['Month'], y=d['Consumption_kWh'],
                name=str(yr), mode='lines+markers',
                line=dict(color=YEAR_COLORS.get(yr, '#fff'), width=2.5, dash=dash_map.get(yr, 'solid')),
                marker=dict(size=6, color=YEAR_COLORS.get(yr, '#fff')),
                hovertemplate=f'<b>{yr}</b><br>الشهر: %{{x}}<br>الاستهلاك: %{{y:,.0f}} كيلوواط<extra></extra>'
            ))

        fig_trend.update_layout(**dark_layout(height=300, showlegend=True))
        fig_trend.update_xaxes(**dark_xaxis(
            tickmode='array', tickvals=list(range(1, 13)),
            ticktext=[MONTH_NAMES[i] for i in range(1, 13)]
        ))
        fig_trend.update_yaxes(**dark_yaxis(tickformat=',.0f'))
        fig_trend.update_layout(hovermode='x unified')
        st.plotly_chart(fig_trend, use_container_width=True, key="trend_main")

    with col_right:
        st.markdown('<div class="section-header"><span class="section-icon">خريطة</span><h3>توزيع الاستهلاك بالمناطق</h3></div>', unsafe_allow_html=True)

        region_data = df_f[df_f['Year'].isin([2024, 2025])].groupby('Region_Major')['Consumption_kWh'].sum().reset_index()
        region_data = region_data.sort_values('Consumption_kWh', ascending=True)

        fig_reg = go.Figure(go.Bar(
            x=region_data['Consumption_kWh'],
            y=region_data['Region_Major'],
            orientation='h',
            marker=dict(
                color=[REGION_COLORS.get(r, '#8b949e') for r in region_data['Region_Major']],
                line=dict(color='#0d1117', width=1)
            ),
            text=[fmt_num(v) for v in region_data['Consumption_kWh']],
            textposition='outside',
            textfont=dict(color='#8b949e', size=11),
            hovertemplate='<b>%{y}</b><br>الاستهلاك: %{x:,.0f} كيلوواط<extra></extra>'
        ))
        fig_reg.update_layout(**dark_layout(height=300, showlegend=False))
        fig_reg.update_xaxes(**dark_xaxis(tickformat=',.0f'))
        fig_reg.update_yaxes(**dark_yaxis())
        st.plotly_chart(fig_reg, use_container_width=True, key="reg_bar")

    # مقارنة شهرية 2024 vs 2025
    st.markdown('<div class="section-header"><span class="section-icon">مقارنة</span><h3>مقارنة الاستهلاك الشهري 2024 مقابل 2025</h3></div>', unsafe_allow_html=True)

    col_comp, col_season = st.columns([3, 2])

    with col_comp:
        comp_data = df_f[df_f['Year'].isin([2024, 2025])].groupby(['Year', 'Month'])['Consumption_kWh'].sum().reset_index()
        fig_comp = go.Figure()
        for yr in [2024, 2025]:
            d = comp_data[comp_data['Year'] == yr].sort_values('Month')
            fig_comp.add_trace(go.Bar(
                x=d['Month'], y=d['Consumption_kWh'],
                name=str(yr),
                marker=dict(color=YEAR_COLORS.get(yr, '#fff'), opacity=0.85),
                hovertemplate=f'<b>{yr}</b><br>الشهر: %{{x}}<br>%{{y:,.0f}} كيلوواط<extra></extra>'
            ))
        fig_comp.update_layout(**dark_layout(height=280, showlegend=True))
        fig_comp.update_layout(barmode='group')
        fig_comp.update_xaxes(**dark_xaxis(
            tickmode='array', tickvals=list(range(1, 13)),
            ticktext=[MONTH_NAMES[i] for i in range(1, 13)]
        ))
        fig_comp.update_yaxes(**dark_yaxis(tickformat=',.0f'))
        st.plotly_chart(fig_comp, use_container_width=True, key="comp_bar")

    with col_season:
        def get_season(m):
            if m in [12, 1, 2]: return 'الشتاء'
            elif m in [3, 4, 5]: return 'الربيع'
            elif m in [6, 7, 8]: return 'الصيف'
            else: return 'الخريف'

        season_data = df_f[df_f['Year'].isin([2024, 2025])].copy()
        season_data['Season'] = season_data['Month'].map(get_season)
        season_agg = season_data.groupby('Season')['Consumption_kWh'].sum().reset_index()
        season_order = ['الشتاء', 'الربيع', 'الصيف', 'الخريف']
        season_colors = ['#58a6ff', '#3fb950', '#f85149', '#d29922']
        season_agg['order'] = season_agg['Season'].map({s: i for i, s in enumerate(season_order)})
        season_agg = season_agg.sort_values('order')

        fig_season = go.Figure(go.Pie(
            labels=season_agg['Season'],
            values=season_agg['Consumption_kWh'],
            hole=0.55,
            marker=dict(colors=season_colors, line=dict(color='#0d1117', width=2)),
            textinfo='label+percent',
            textfont=dict(color='#e6edf3', size=11),
            hovertemplate='<b>%{label}</b><br>%{value:,.0f} كيلوواط<br>%{percent}<extra></extra>'
        ))
        fig_season.update_layout(**dark_layout(height=280, showlegend=False))
        fig_season.add_annotation(
            text='الفصول', x=0.5, y=0.5, font_size=13,
            font_color='#8b949e', showarrow=False
        )
        st.plotly_chart(fig_season, use_container_width=True, key="season_pie")

    # KPI Sparklines
    st.markdown('<div class="section-header"><span class="section-icon">اتجاه</span><h3>مؤشرات الأداء الشهرية</h3></div>', unsafe_allow_html=True)

    monthly_24 = df_f[df_f['Year'] == 2024].groupby('Month')['Consumption_kWh'].sum().reindex(range(1, 13), fill_value=0).values.tolist()
    monthly_25 = df_f[df_f['Year'] == 2025].groupby('Month')['Consumption_kWh'].sum().reindex(range(1, 13), fill_value=0).values.tolist()
    monthly_26_actual = df_f[df_f['Year'] == 2026].groupby('Month')['Consumption_kWh'].sum().reindex(range(1, 13), fill_value=0).values.tolist()

    sp_col1, sp_col2, sp_col3 = st.columns(3)
    with sp_col1:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">اتجاه 2024 الشهري</div><div class="kpi-value blue">{fmt_num(total_24)}</div></div>', unsafe_allow_html=True)
        st.plotly_chart(sparkline_fig(monthly_24, '#58a6ff'), use_container_width=True, key="sp1")
    with sp_col2:
        st.markdown(f'<div class="kpi-card green"><div class="kpi-label">اتجاه 2025 الشهري</div><div class="kpi-value green">{fmt_num(total_25)}</div></div>', unsafe_allow_html=True)
        st.plotly_chart(sparkline_fig(monthly_25, '#3fb950'), use_container_width=True, key="sp2")
    with sp_col3:
        st.markdown(f'<div class="kpi-card orange"><div class="kpi-label">اتجاه 2026 الفعلي (Q1)</div><div class="kpi-value orange">{fmt_num(total_26_actual)}</div></div>', unsafe_allow_html=True)
        st.plotly_chart(sparkline_fig(monthly_26_actual, '#d29922'), use_container_width=True, key="sp3")

# ══════════════════════════════════════════════
# تبويب 2: التحليل الإحصائي
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header"><span class="section-icon">تحليل</span><h3>التحليل الإحصائي المتقدم</h3></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        cat_data = df_f[df_f['Year'].isin([2024, 2025])].groupby('Account_Category')['Consumption_kWh'].sum().reset_index()
        fig_cat = go.Figure(go.Pie(
            labels=cat_data['Account_Category'],
            values=cat_data['Consumption_kWh'],
            hole=0.5,
            marker=dict(colors=['#c0392b', '#484f58'], line=dict(color='#0d1117', width=2)),
            textinfo='label+percent',
            textfont=dict(color='#e6edf3', size=11)
        ))
        fig_cat.update_layout(**dark_layout(height=250, title='توزيع الاستهلاك حسب نوع الحساب', showlegend=False))
        st.plotly_chart(fig_cat, use_container_width=True, key="cat_pie")

    with col_b:
        dyn_yr = max(selected_years)
        region_ca = df_f[df_f['Year'] == dyn_yr].groupby('Region_Major')['Collective_CA'].nunique().reset_index()
        fig_rca = go.Figure(go.Bar(
            x=region_ca['Region_Major'],
            y=region_ca['Collective_CA'],
            marker=dict(color=[REGION_COLORS.get(r, '#8b949e') for r in region_ca['Region_Major']]),
            text=region_ca['Collective_CA'],
            textposition='outside',
            textfont=dict(color='#8b949e')
        ))
        fig_rca.update_layout(**dark_layout(height=250, title=f'عدد الحسابات التجميعية بالمنطقة ({dyn_yr})', showlegend=False))
        fig_rca.update_xaxes(**dark_xaxis())
        fig_rca.update_yaxes(**dark_yaxis())
        st.plotly_chart(fig_rca, use_container_width=True, key="rca_bar")

    # عدد العدادات لكل حساب تجميعي (ديناميكي حسب السنة)
    st.markdown(f'<div class="section-header"><span class="section-icon">عدادات</span><h3>عدد العدادات لكل حساب تجميعي ({dyn_yr})</h3></div>', unsafe_allow_html=True)

    meters_per_ca = df_f[df_f['Year'] == dyn_yr].groupby('Collective_CA').agg(
        عدد_العدادات=('Contract_Account', 'nunique'),
        الاستهلاك=('Consumption_kWh', 'sum'),
        المبلغ=('Bill_Amount', 'sum'),
        المنطقة=('Region_Major', 'first')
    ).reset_index().sort_values('عدد_العدادات', ascending=False)

    meters_col_l, meters_col_r = st.columns([3, 2])
    with meters_col_l:
        fig_meters = go.Figure(go.Bar(
            x=meters_per_ca['عدد_العدادات'],
            y=meters_per_ca['Collective_CA'],
            orientation='h',
            marker=dict(
                color=[REGION_COLORS.get(r, '#8b949e') for r in meters_per_ca['المنطقة']],
                opacity=0.85, line=dict(color='#0d1117', width=1)
            ),
            text=meters_per_ca['عدد_العدادات'],
            textposition='outside',
            textfont=dict(color='#8b949e', size=9),
            hovertemplate='<b>حساب: %{y}</b><br>عدد العدادات: %{x}<extra></extra>'
        ))
        fig_meters.update_layout(**dark_layout(height=max(300, len(meters_per_ca) * 22), showlegend=False,
            title=f'عدد العدادات لكل حساب تجميعي ({dyn_yr})'))
        fig_meters.update_xaxes(**dark_xaxis())
        fig_meters.update_yaxes(**dark_yaxis(tickfont=dict(color='#e6edf3', size=9)))
        st.plotly_chart(fig_meters, use_container_width=True, key="meters_bar")

    with meters_col_r:
        st.dataframe(
            meters_per_ca[['Collective_CA', 'عدد_العدادات', 'المنطقة']].style.format({
                'عدد_العدادات': '{:,}'
            }).background_gradient(subset=['عدد_العدادات'], cmap='Blues'),
            use_container_width=True, height=400
        )

    # معدلات النمو
    st.markdown('<div class="section-header"><span class="section-icon">نمو</span><h3>معدلات النمو الشهرية (2024 - 2025)</h3></div>', unsafe_allow_html=True)

    growth_24 = df_f[df_f['Year'] == 2024].groupby('Month')['Consumption_kWh'].sum()
    growth_25 = df_f[df_f['Year'] == 2025].groupby('Month')['Consumption_kWh'].sum()
    common_months = sorted(set(growth_24.index) & set(growth_25.index))

    if common_months:
        growth_pct = [delta_pct(growth_25.get(m, 0), growth_24.get(m, 0)) for m in common_months]
        colors_growth = ['#3fb950' if g >= 0 else '#f85149' for g in growth_pct]

        fig_growth = go.Figure(go.Bar(
            x=[MONTH_NAMES[m] for m in common_months],
            y=growth_pct,
            marker=dict(color=colors_growth, line=dict(color='#0d1117', width=1)),
            text=[f'{g:+.1f}%' for g in growth_pct],
            textposition='outside',
            textfont=dict(color='#8b949e', size=10),
            hovertemplate='%{x}<br>معدل النمو: %{y:.1f}%<extra></extra>'
        ))
        fig_growth.add_hline(y=0, line_color='#484f58', line_width=1)
        fig_growth.update_layout(**dark_layout(height=280, showlegend=False))
        fig_growth.update_xaxes(**dark_xaxis())
        fig_growth.update_yaxes(**dark_yaxis(ticksuffix='%'))
        st.plotly_chart(fig_growth, use_container_width=True, key="growth_bar")

    # أعلى وأدنى حسابات
    col_up, col_down = st.columns(2)

    with col_up:
        st.markdown(f'<div class="section-header"><span class="section-icon">أعلى</span><h3>أعلى 10 حسابات تجميعية استهلاكاً ({dyn_yr})</h3></div>', unsafe_allow_html=True)
        top_ca = df_f[df_f['Year'] == dyn_yr].groupby('Collective_CA').agg(
            Consumption=('Consumption_kWh', 'sum'),
            Bill=('Bill_Amount', 'sum')
        ).nlargest(10, 'Consumption').reset_index()
        fig_up = go.Figure(go.Bar(
            x=top_ca['Consumption'],
            y=top_ca['Collective_CA'],
            orientation='h',
            marker=dict(color='#f85149', opacity=0.8),
            text=[f"{fmt_num(v)} | {fmt_num(b,'SAR')}" for v, b in zip(top_ca['Consumption'], top_ca['Bill'])],
            textposition='outside',
            textfont=dict(color='#8b949e', size=9),
            hovertemplate='<b>حساب: %{y}</b><br>الاستهلاك: %{x:,.0f} kWh<extra></extra>'
        ))
        fig_up.update_layout(**dark_layout(height=360, showlegend=False))
        fig_up.update_xaxes(**dark_xaxis(tickformat=',.0f'))
        fig_up.update_yaxes(**dark_yaxis(tickfont=dict(color='#e6edf3', size=10)))
        st.plotly_chart(fig_up, use_container_width=True, key="top_ca")

    with col_down:
        st.markdown(f'<div class="section-header"><span class="section-icon">أدنى</span><h3>أدنى 10 حسابات تجميعية استهلاكاً ({dyn_yr})</h3></div>', unsafe_allow_html=True)
        bot_ca = df_f[(df_f['Year'] == dyn_yr) & (df_f['Consumption_kWh'] > 0)].groupby('Collective_CA').agg(
            Consumption=('Consumption_kWh', 'sum'),
            Bill=('Bill_Amount', 'sum')
        ).nsmallest(10, 'Consumption').reset_index()
        fig_down = go.Figure(go.Bar(
            x=bot_ca['Consumption'],
            y=bot_ca['Collective_CA'],
            orientation='h',
            marker=dict(color='#3fb950', opacity=0.8),
            text=[f"{fmt_num(v)} | {fmt_num(b,'SAR')}" for v, b in zip(bot_ca['Consumption'], bot_ca['Bill'])],
            textposition='outside',
            textfont=dict(color='#8b949e', size=9),
            hovertemplate='<b>حساب: %{y}</b><br>الاستهلاك: %{x:,.0f} kWh<extra></extra>'
        ))
        fig_down.update_layout(**dark_layout(height=360, showlegend=False))
        fig_down.update_xaxes(**dark_xaxis(tickformat=',.0f'))
        fig_down.update_yaxes(**dark_yaxis(tickfont=dict(color='#e6edf3', size=10)))
        st.plotly_chart(fig_down, use_container_width=True, key="bot_ca")

    # توزيع المبالغ بالريال حسب الحسابات التجميعية
    st.markdown(f'<div class="section-header"><span class="section-icon">SAR</span><h3>توزيع المبالغ بالريال حسب الحسابات التجميعية ({dyn_yr})</h3></div>', unsafe_allow_html=True)
    bill_dist = df_f[df_f['Year'] == dyn_yr].groupby('Collective_CA').agg(
        Bill=('Bill_Amount', 'sum'),
        Consumption=('Consumption_kWh', 'sum')
    ).reset_index().sort_values('Bill', ascending=False).head(20)

    fig_bill_dist = go.Figure()
    fig_bill_dist.add_trace(go.Bar(
        x=bill_dist['Collective_CA'],
        y=bill_dist['Bill'],
        name='المبلغ (SAR)',
        marker=dict(color='#d29922', opacity=0.85),
        hovertemplate='<b>حساب: %{x}</b><br>المبلغ: %{y:,.0f} SAR<extra></extra>'
    ))
    fig_bill_dist.add_trace(go.Scatter(
        x=bill_dist['Collective_CA'],
        y=bill_dist['Consumption'],
        name='الاستهلاك (kWh)',
        mode='lines+markers',
        line=dict(color='#58a6ff', width=2),
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='<b>حساب: %{x}</b><br>الاستهلاك: %{y:,.0f} kWh<extra></extra>'
    ))
    fig_bill_dist.update_layout(
        **dark_layout(height=300, showlegend=True),
        yaxis2=dict(
            overlaying='y', side='left',
            gridcolor='#21262d', linecolor='#30363d',
            tickfont=dict(color='#58a6ff', size=10),
            title=dict(text='استهلاك (kWh)', font=dict(color='#58a6ff', size=10))
        ),
        yaxis=dict(title=dict(text='المبلغ (SAR)', font=dict(color='#d29922', size=10)),
                   tickfont=dict(color='#d29922'))
    )
    fig_bill_dist.update_xaxes(**dark_xaxis(tickangle=-45, tickfont=dict(color='#8b949e', size=9)))
    st.plotly_chart(fig_bill_dist, use_container_width=True, key="bill_dist")

# ══════════════════════════════════════════════
# تبويب 3: إدارة الأصول
# ══════════════════════════════════════════════
with tab3:
    # بحث / Dropdown للحساب التجميعي
    st.markdown('<div class="section-header"><span class="section-icon">بحث</span><h3>بحث عن حساب تجميعي</h3></div>', unsafe_allow_html=True)

    all_ca_list = sorted(df['Collective_CA'].unique().tolist())
    search_ca = st.selectbox(
        "اختر أو ابحث عن حساب تجميعي:",
        options=["اختر حسابًا..."] + all_ca_list,
        key="search_ca_select"
    )

    if search_ca != "اختر حسابًا...":
        ca_detail = df[df['Collective_CA'] == search_ca]
        ca_total_kwh = ca_detail['Consumption_kWh'].sum()
        ca_total_sar = ca_detail['Bill_Amount'].sum()
        ca_num_contracts = ca_detail['Contract_Account'].nunique()
        ca_avg_kwh = ca_detail['Consumption_kWh'].mean()
        ca_region = ca_detail['Region_Major'].mode()[0] if len(ca_detail) > 0 else '-'
        ca_city = ca_detail['Region_City'].mode()[0] if 'Region_City' in ca_detail.columns and len(ca_detail) > 0 else '-'

        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        with d_col1:
            st.markdown(kpi_card("إجمالي الاستهلاك", fmt_num(ca_total_kwh, 'kWh'), None, 'blue', ''), unsafe_allow_html=True)
        with d_col2:
            st.markdown(kpi_card("إجمالي المبلغ", fmt_num(ca_total_sar, 'SAR'), None, 'orange', ''), unsafe_allow_html=True)
        with d_col3:
            st.markdown(kpi_card("عدد العدادات", str(ca_num_contracts), None, 'purple', ''), unsafe_allow_html=True)
        with d_col4:
            st.markdown(kpi_card("متوسط الاستهلاك", fmt_num(ca_avg_kwh, 'kWh'), None, 'green', ''), unsafe_allow_html=True)

        st.markdown(f"""
        <div class="alert-card info" style="margin:10px 0 15px;">
            <div style="color:#58a6ff; font-weight:600; font-size:14px;">الحساب: {search_ca}</div>
            <div style="color:#8b949e; font-size:12px; margin-top:4px;">المنطقة: {ca_region} | المدينة: {ca_city} | إجمالي العدادات: {ca_num_contracts}</div>
        </div>
        """, unsafe_allow_html=True)

        ca_monthly = ca_detail.groupby(['Year', 'Month']).agg(
            Consumption=('Consumption_kWh', 'sum'),
            Bill=('Bill_Amount', 'sum')
        ).reset_index()
        fig_ca_detail = go.Figure()
        for yr in sorted(ca_monthly['Year'].unique()):
            d = ca_monthly[ca_monthly['Year'] == yr].sort_values('Month')
            fig_ca_detail.add_trace(go.Scatter(
                x=d['Month'], y=d['Consumption'],
                name=f'{yr} - kWh', mode='lines+markers',
                line=dict(color=YEAR_COLORS.get(yr, '#fff'), width=2.5),
                marker=dict(size=7),
                hovertemplate=f'<b>{yr}</b><br>الشهر: %{{x}}<br>الاستهلاك: %{{y:,.0f}} kWh<extra></extra>'
            ))
        fig_ca_detail.update_layout(**dark_layout(height=280, showlegend=True,
            title=f'استهلاك الحساب {search_ca} - تفصيل شهري'))
        fig_ca_detail.update_xaxes(**dark_xaxis(
            tickmode='array', tickvals=list(range(1, 13)),
            ticktext=[MONTH_NAMES[i] for i in range(1, 13)]
        ))
        fig_ca_detail.update_yaxes(**dark_yaxis(tickformat=',.0f'))
        st.plotly_chart(fig_ca_detail, use_container_width=True, key="ca_detail_chart")

        st.markdown(f'<div class="section-header"><span class="section-icon">عدادات</span><h3>جميع العدادات المرتبطة بالحساب {search_ca} ({ca_num_contracts} عداد)</h3></div>', unsafe_allow_html=True)
        sub_tbl = ca_detail.groupby('Contract_Account').agg(
            الاستهلاك_kWh=('Consumption_kWh', 'sum'),
            المبلغ_SAR=('Bill_Amount', 'sum'),
            عدد_السجلات=('Month', 'count'),
            المنطقة=('Region_Major', 'first'),
            المدينة=('Region_City', 'first')
        ).reset_index().sort_values('الاستهلاك_kWh', ascending=False)
        sub_tbl.index = range(1, len(sub_tbl) + 1)
        st.dataframe(
            sub_tbl.style.format({
                'الاستهلاك_kWh': '{:,.0f}',
                'المبلغ_SAR': '{:,.2f}'
            }).background_gradient(subset=['الاستهلاك_kWh'], cmap='Blues'),
            use_container_width=True, height=350
        )
    else:
        st.info("اختر حسابًا تجميعيًا من القائمة أعلاه لعرض تفاصيله وجميع عداداته")

    st.markdown("<br>", unsafe_allow_html=True)

    # جدول الحسابات ذات الاستهلاك المنخفض
    st.markdown('<div class="section-header"><span class="section-icon">مراجعة</span><h3>حسابات ذات استهلاك منخفض (0 - 1.67 kWh) وبدون مبالغ</h3></div>', unsafe_allow_html=True)

    low_cons_df = df[(df['Consumption_kWh'] >= 0) & (df['Consumption_kWh'] <= 1.67) & (df['Bill_Amount'] == 0)].copy()
    if len(low_cons_df) > 0:
        low_cons_summary = low_cons_df.groupby('Contract_Account').agg(
            الحساب_التجميعي=('Collective_CA', 'first'),
            المنطقة=('Region_Major', 'first'),
            المدينة=('Region_City', 'first'),
            الاستهلاك_الإجمالي_kWh=('Consumption_kWh', 'sum'),
            أقصى_استهلاك_kWh=('Consumption_kWh', 'max'),
            عدد_الأشهر=('Month', 'count'),
            السنة=('Year', lambda x: ', '.join(sorted(x.astype(str).unique())))
        ).reset_index().sort_values('الاستهلاك_الإجمالي_kWh', ascending=False)
        low_cons_summary.index = range(1, len(low_cons_summary) + 1)

        lc_col1, lc_col2, lc_col3 = st.columns(3)
        with lc_col1:
            st.markdown(kpi_card("عدد الحسابات الفرعية", str(len(low_cons_summary)), None, 'orange', ''), unsafe_allow_html=True)
        with lc_col2:
            st.markdown(kpi_card("إجمالي السجلات", str(len(low_cons_df)), None, 'red', ''), unsafe_allow_html=True)
        with lc_col3:
            st.markdown(kpi_card("إجمالي الاستهلاك", fmt_num(low_cons_df['Consumption_kWh'].sum(), 'kWh'), None, 'purple', ''), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            low_cons_summary.style.format({
                'الاستهلاك_الإجمالي_kWh': '{:.4f}',
                'أقصى_استهلاك_kWh': '{:.4f}'
            }).background_gradient(subset=['الاستهلاك_الإجمالي_kWh'], cmap='Oranges'),
            use_container_width=True, height=400
        )
    else:
        st.info("لا توجد حسابات ذات استهلاك في النطاق 0-1.67 kWh بدون مبالغ في البيانات الحالية.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-icon">جدول</span><h3>تحليل الحسابات التجميعية</h3></div>', unsafe_allow_html=True)

    ca_summary = df_f[df_f['Year'].isin([2024, 2025])].groupby('Collective_CA').agg(
        استهلاك_2024=('Consumption_kWh', lambda x: x[df_f.loc[x.index, 'Year'] == 2024].sum()),
        استهلاك_2025=('Consumption_kWh', lambda x: x[df_f.loc[x.index, 'Year'] == 2025].sum()),
        المنطقة=('Region_Major', 'first'),
        عدد_الفروع=('Contract_Account', 'nunique')
    ).reset_index()
    ca_summary['التغيير_%'] = ca_summary.apply(
        lambda r: delta_pct(r['استهلاك_2025'], r['استهلاك_2024']), axis=1
    )
    ca_summary = ca_summary.sort_values('استهلاك_2025', ascending=False)

    col_tbl, col_map = st.columns([3, 2])
    with col_tbl:
        st.dataframe(
            ca_summary.style.format({
                'استهلاك_2024': '{:,.0f}',
                'استهلاك_2025': '{:,.0f}',
                'التغيير_%': '{:+.1f}%'
            }).background_gradient(subset=['التغيير_%'], cmap='RdYlGn'),
            use_container_width=True,
            height=400
        )

    with col_map:
        region_map = df_f[df_f['Year'].isin([2024, 2025])].groupby('Region_Major')['Consumption_kWh'].sum().reset_index()
        region_map['النسبة'] = region_map['Consumption_kWh'] / region_map['Consumption_kWh'].sum() * 100

        fig_map = go.Figure(go.Bar(
            x=region_map['النسبة'],
            y=region_map['Region_Major'],
            orientation='h',
            marker=dict(
                color=[REGION_COLORS.get(r, '#8b949e') for r in region_map['Region_Major']],
                line=dict(color='#0d1117', width=1)
            ),
            text=[f'{p:.1f}%' for p in region_map['النسبة']],
            textposition='outside',
            textfont=dict(color='#8b949e', size=11)
        ))
        fig_map.update_layout(**dark_layout(height=400, title='الحصة النسبية للمناطق', showlegend=False))
        fig_map.update_xaxes(**dark_xaxis(ticksuffix='%'))
        fig_map.update_yaxes(**dark_yaxis())
        st.plotly_chart(fig_map, use_container_width=True, key="region_map")

    # الحسابات المرشحة للمراجعة
    st.markdown('<div class="section-header"><span class="section-icon">تنبيه</span><h3>الحسابات المرشحة للمراجعة</h3></div>', unsafe_allow_html=True)

    col_alert1, col_alert2, col_alert3 = st.columns(3)

    with col_alert1:
        st.markdown("**ارتفاع كبير (أكثر من 50%)**")
        high_growth = ca_summary[ca_summary['التغيير_%'] > 50].head(5)
        for _, row in high_growth.iterrows():
            st.markdown(f"""
            <div class="alert-card danger">
                <div>
                    <div style="color:#f85149; font-weight:600; font-size:13px;">حساب {row['Collective_CA']}</div>
                    <div style="color:#8b949e; font-size:11px;">{row['المنطقة']} | +{row['التغيير_%']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_alert2:
        st.markdown("**انخفاض كبير (أكثر من 30%)**")
        low_growth = ca_summary[ca_summary['التغيير_%'] < -30].head(5)
        for _, row in low_growth.iterrows():
            st.markdown(f"""
            <div class="alert-card warning">
                <div>
                    <div style="color:#d29922; font-weight:600; font-size:13px;">حساب {row['Collective_CA']}</div>
                    <div style="color:#8b949e; font-size:11px;">{row['المنطقة']} | {row['التغيير_%']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_alert3:
        st.markdown("**استهلاك صفري مع فاتورة**")
        zero_cons = df_f[(df_f['Consumption_kWh'] == 0) & (df_f['Bill_Amount'] > 0)].groupby('Contract_Account').agg(
            إجمالي_الفاتورة=('Bill_Amount', 'sum'),
            عدد_الأشهر=('Month', 'count')
        ).reset_index().head(5)
        for _, row in zero_cons.iterrows():
            st.markdown(f"""
            <div class="alert-card info">
                <div>
                    <div style="color:#58a6ff; font-weight:600; font-size:13px;">حساب {row['Contract_Account']}</div>
                    <div style="color:#8b949e; font-size:11px;">فاتورة: {row['إجمالي_الفاتورة']:.2f} ريال | {row['عدد_الأشهر']} أشهر</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # تحليل الحسابات التجميعية الإضافية
    st.markdown('<div class="section-header"><span class="section-icon">إضافي</span><h3>الحسابات التجميعية الإضافية</h3></div>', unsafe_allow_html=True)

    add_ca = df_f[df_f['Account_Category'] == 'حساب تجميعي إضافي']
    if len(add_ca) > 0:
        add_summary = add_ca.groupby(['Collective_CA', 'Year'])['Consumption_kWh'].sum().reset_index()
        fig_add = go.Figure()
        for yr in sorted(add_summary['Year'].unique()):
            d = add_summary[add_summary['Year'] == yr]
            fig_add.add_trace(go.Bar(
                x=d['Collective_CA'], y=d['Consumption_kWh'],
                name=str(yr),
                marker=dict(color=YEAR_COLORS.get(yr, '#fff'), opacity=0.8)
            ))
        fig_add.update_layout(**dark_layout(height=300, showlegend=True))
        fig_add.update_layout(barmode='group')
        fig_add.update_xaxes(**dark_xaxis())
        fig_add.update_yaxes(**dark_yaxis(tickformat=',.0f'))
        st.plotly_chart(fig_add, use_container_width=True, key="add_ca")
    else:
        st.info("لا توجد حسابات تجميعية إضافية في البيانات المفلترة الحالية.")

# ══════════════════════════════════════════════
# تبويب: التحليل الجغرافي
# ══════════════════════════════════════════════
with tab_geo:
    st.markdown('<div class="section-header"><span class="section-icon">جغرافي</span><h3>التحليل الجغرافي حسب المناطق والمدن</h3></div>', unsafe_allow_html=True)

    geo_df = df_f.copy()

    geo_total_kwh = geo_df['Consumption_kWh'].sum()
    geo_total_sar = geo_df['Bill_Amount'].sum()
    geo_num_cities = geo_df['Region_City'].nunique() if 'Region_City' in geo_df.columns else 0
    geo_num_regions = geo_df['Region_Major'].nunique()

    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    with g_col1:
        st.markdown(kpi_card("إجمالي الاستهلاك", fmt_num(geo_total_kwh, 'kWh'), None, 'blue', ''), unsafe_allow_html=True)
    with g_col2:
        st.markdown(kpi_card("إجمالي الفواتير", fmt_num(geo_total_sar, 'SAR'), None, 'orange', ''), unsafe_allow_html=True)
    with g_col3:
        st.markdown(kpi_card("عدد المدن", str(geo_num_cities), None, 'purple', ''), unsafe_allow_html=True)
    with g_col4:
        st.markdown(kpi_card("المناطق الرئيسية", str(geo_num_regions), None, 'green', ''), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header"><span class="section-icon">مناطق</span><h3>استهلاك ومبالغ الكهرباء حسب المنطقة الرئيسية</h3></div>', unsafe_allow_html=True)

    region_geo = geo_df.groupby('Region_Major').agg(
        Consumption=('Consumption_kWh', 'sum'),
        Bill=('Bill_Amount', 'sum'),
        Accounts=('Contract_Account', 'nunique'),
        Collective=('Collective_CA', 'nunique')
    ).reset_index().sort_values('Consumption', ascending=False)

    geo_col_left, geo_col_right = st.columns([3, 2])

    with geo_col_left:
        fig_geo_bar = go.Figure()
        fig_geo_bar.add_trace(go.Bar(
            x=region_geo['Region_Major'],
            y=region_geo['Consumption'],
            name='الاستهلاك (kWh)',
            marker=dict(color=[REGION_COLORS.get(r, '#8b949e') for r in region_geo['Region_Major']], opacity=0.85),
            text=[fmt_num(v) for v in region_geo['Consumption']],
            textposition='outside',
            textfont=dict(color='#8b949e', size=10),
            hovertemplate='<b>%{x}</b><br>استهلاك: %{y:,.0f} kWh<extra></extra>'
        ))
        fig_geo_bar.add_trace(go.Scatter(
            x=region_geo['Region_Major'],
            y=region_geo['Bill'],
            name='المبلغ (SAR)',
            mode='lines+markers',
            line=dict(color='#d29922', width=2.5),
            marker=dict(size=9, symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>المبلغ: %{y:,.0f} SAR<extra></extra>'
        ))
        fig_geo_bar.update_layout(
            **dark_layout(height=320, showlegend=True),
            yaxis2=dict(
                overlaying='y', side='right',
                gridcolor='#21262d', linecolor='#30363d',
                tickfont=dict(color='#d29922', size=10),
                title=dict(text='المبلغ (SAR)', font=dict(color='#d29922', size=10))
            ),
            yaxis=dict(
                title=dict(text='الاستهلاك (kWh)', font=dict(color='#8b949e', size=10)),
                tickfont=dict(color='#8b949e')
            )
        )
        fig_geo_bar.update_xaxes(**dark_xaxis())
        st.plotly_chart(fig_geo_bar, use_container_width=True, key="geo_bar")

    with geo_col_right:
        fig_geo_pie = go.Figure(go.Pie(
            labels=region_geo['Region_Major'],
            values=region_geo['Consumption'],
            hole=0.5,
            marker=dict(
                colors=[REGION_COLORS.get(r, '#8b949e') for r in region_geo['Region_Major']],
                line=dict(color='#0d1117', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(color='#e6edf3', size=11),
            hovertemplate='<b>%{label}</b><br>استهلاك: %{value:,.0f} kWh<br>%{percent}<extra></extra>'
        ))
        fig_geo_pie.update_layout(**dark_layout(height=320, showlegend=False))
        fig_geo_pie.add_annotation(
            text='توزيع', x=0.5, y=0.5, font_size=13,
            font_color='#8b949e', showarrow=False
        )
        st.plotly_chart(fig_geo_pie, use_container_width=True, key="geo_pie")

    if 'Region_City' in geo_df.columns:
        st.markdown('<div class="section-header"><span class="section-icon">مدن</span><h3>تحليل استهلاك المدن والمناطق</h3></div>', unsafe_allow_html=True)

        city_geo = geo_df.groupby('Region_City').agg(
            Consumption=('Consumption_kWh', 'sum'),
            Bill=('Bill_Amount', 'sum'),
            Accounts=('Contract_Account', 'nunique')
        ).reset_index().sort_values('Consumption', ascending=False).head(20)

        city_col_l, city_col_r = st.columns(2)

        with city_col_l:
            fig_city_kwh = go.Figure(go.Bar(
                x=city_geo['Consumption'],
                y=city_geo['Region_City'],
                orientation='h',
                marker=dict(color='#1f6feb', opacity=0.85, line=dict(color='#0d1117', width=1)),
                text=[fmt_num(v) for v in city_geo['Consumption']],
                textposition='outside',
                textfont=dict(color='#8b949e', size=9),
                hovertemplate='<b>%{y}</b><br>استهلاك: %{x:,.0f} kWh<extra></extra>'
            ))
            fig_city_kwh.update_layout(**dark_layout(height=400, title='أعلى 20 مدينة استهلاكاً (kWh)', showlegend=False))
            fig_city_kwh.update_xaxes(**dark_xaxis(tickformat=',.0f'))
            fig_city_kwh.update_yaxes(**dark_yaxis(tickfont=dict(color='#e6edf3', size=10)))
            st.plotly_chart(fig_city_kwh, use_container_width=True, key="city_kwh")

        with city_col_r:
            fig_city_sar = go.Figure(go.Bar(
                x=city_geo['Bill'],
                y=city_geo['Region_City'],
                orientation='h',
                marker=dict(color='#d29922', opacity=0.85, line=dict(color='#0d1117', width=1)),
                text=[fmt_num(v, 'SAR') for v in city_geo['Bill']],
                textposition='outside',
                textfont=dict(color='#8b949e', size=9),
                hovertemplate='<b>%{y}</b><br>المبلغ: %{x:,.0f} SAR<extra></extra>'
            ))
            fig_city_sar.update_layout(**dark_layout(height=400, title='أعلى 20 مدينة مبالغاً (SAR)', showlegend=False))
            fig_city_sar.update_xaxes(**dark_xaxis(tickformat=',.0f'))
            fig_city_sar.update_yaxes(**dark_yaxis(tickfont=dict(color='#e6edf3', size=10)))
            st.plotly_chart(fig_city_sar, use_container_width=True, key="city_sar")

    st.markdown('<div class="section-header"><span class="section-icon">ملخص</span><h3>جدول ملخص المناطق</h3></div>', unsafe_allow_html=True)
    region_tbl = region_geo.copy()
    region_tbl.columns = ['المنطقة', 'الاستهلاك (kWh)', 'المبلغ (SAR)', 'عدد الحسابات التعاقدية', 'عدد الحسابات التجميعية']
    region_tbl['نسبة الاستهلاك %'] = (region_tbl['الاستهلاك (kWh)'] / region_tbl['الاستهلاك (kWh)'].sum() * 100).round(1)
    st.dataframe(
        region_tbl.style.format({
            'الاستهلاك (kWh)': '{:,.0f}',
            'المبلغ (SAR)': '{:,.2f}',
            'نسبة الاستهلاك %': '{:.1f}%'
        }).background_gradient(subset=['الاستهلاك (kWh)'], cmap='Reds'),
        use_container_width=True
    )

# ══════════════════════════════════════════════
# تبويب 4: توقعات 2026
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header"><span class="section-icon">توقعات</span><h3>نموذج التنبؤ بالاستهلاك 2026</h3></div>', unsafe_allow_html=True)

    pred_monthly = pred_df.groupby(['Month', 'Type'])['Predicted_Consumption'].sum().reset_index()
    actual_q1 = pred_monthly[pred_monthly['Type'] == 'فعلي']['Predicted_Consumption'].sum()
    predicted_q2_q4 = pred_monthly[pred_monthly['Type'] == 'متوقع']['Predicted_Consumption'].sum()
    total_2026 = actual_q1 + predicted_q2_q4

    q1_comp = comp_df.groupby('Month').agg(
        فعلي=('Consumption_kWh', 'sum'),
        متوقع=('Predicted_Consumption', 'sum')
    ).reset_index()
    q1_accuracy = 100 - abs(q1_comp['فعلي'].sum() - q1_comp['متوقع'].sum()) / q1_comp['فعلي'].sum() * 100 if q1_comp['فعلي'].sum() > 0 else 0

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(kpi_card("Q1 2026 الفعلي", fmt_num(actual_q1), None, 'green', ''), unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(kpi_card("Q2-Q4 المتوقع", fmt_num(predicted_q2_q4), None, 'orange', ''), unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(kpi_card("إجمالي 2026 المتوقع", fmt_num(total_2026), None, 'blue', ''), unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(kpi_card("دقة النموذج Q1", f"{q1_accuracy:.1f}%", None, 'purple', ''), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # قسم معلومات تدريب النموذج
    # ══════════════════════════════════════════════
    st.markdown('<div class="section-header"><span class="section-icon">نموذج</span><h3>معلومات تدريب النموذج</h3></div>', unsafe_allow_html=True)

    # استخراج معلومات النموذج
    if model_metrics:
        best_model_name = model_metrics.get('best_model', 'XGBoost')
        xgb_metrics = model_metrics.get('models', {}).get(best_model_name, {})
        r2_score = xgb_metrics.get('r2', 0.9475)
        rmse_val = xgb_metrics.get('rmse', 1733.8)
        mae_val = xgb_metrics.get('mae', 590.7)
    else:
        best_model_name = 'XGBoost'
        r2_score = 0.9475
        rmse_val = 1733.8
        mae_val = 590.7

    total_records_model = len(df)
    train_records = int(total_records_model * 0.80)
    test_records = total_records_model - train_records

    m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

    with m_col1:
        st.markdown(f"""
        <div class="model-info-card">
            <h4>النموذج المستخدم</h4>
            <div class="model-value" style="color:#58a6ff;">{best_model_name}</div>
            <div class="model-sub">أفضل نموذج من 3 خوارزميات</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="model-info-card">
            <h4>دقة النموذج (R²)</h4>
            <div class="model-value" style="color:#3fb950;">{r2_score*100:.1f}%</div>
            <div class="model-sub">معامل التحديد</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col3:
        st.markdown(f"""
        <div class="model-info-card">
            <h4>دقة التنبؤ Q1 2026</h4>
            <div class="model-value" style="color:#3fb950;">{q1_accuracy:.1f}%</div>
            <div class="model-sub">مقارنة بالفعلي</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col4:
        st.markdown(f"""
        <div class="model-info-card">
            <h4>بيانات التدريب (80%)</h4>
            <div class="model-value" style="color:#d29922;">{train_records:,}</div>
            <div class="model-sub">سجل للتدريب</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col5:
        st.markdown(f"""
        <div class="model-info-card">
            <h4>بيانات الاختبار (20%)</h4>
            <div class="model-value" style="color:#f85149;">{test_records:,}</div>
            <div class="model-sub">سجل للاختبار</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col6:
        st.markdown(f"""
        <div class="model-info-card">
            <h4>متوسط الخطأ (MAE)</h4>
            <div class="model-value" style="color:#bc8cff;">{mae_val:,.0f}</div>
            <div class="model-sub">كيلوواط/ساعة</div>
        </div>
        """, unsafe_allow_html=True)

    # جدول مقارنة النماذج
    if model_metrics and 'models' in model_metrics:
        with st.expander("مقارنة أداء النماذج الثلاثة"):
            models_data = []
            for model_name, metrics in model_metrics['models'].items():
                models_data.append({
                    'النموذج': model_name,
                    'R² Score': f"{metrics.get('r2', 0)*100:.2f}%",
                    'RMSE': f"{metrics.get('rmse', 0):,.1f}",
                    'MAE': f"{metrics.get('mae', 0):,.1f}",
                    'الحالة': 'الأفضل' if model_name == best_model_name else '-'
                })
            models_df = pd.DataFrame(models_data)
            st.dataframe(models_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # الاستهلاك الفعلي والمتوقع 2026
    st.markdown('<div class="section-header"><span class="section-icon">بياني</span><h3>الاستهلاك الفعلي والمتوقع 2026</h3></div>', unsafe_allow_html=True)

    forecast_monthly = pred_df.groupby(['Month', 'Type'])['Predicted_Consumption'].sum().reset_index()
    actual_part = forecast_monthly[forecast_monthly['Type'] == 'فعلي'].sort_values('Month')
    pred_part = forecast_monthly[forecast_monthly['Type'] == 'متوقع'].sort_values('Month')

    hist_2024 = df[df['Year'] == 2024].groupby('Month')['Consumption_kWh'].sum().reset_index()
    hist_2025 = df[df['Year'] == 2025].groupby('Month')['Consumption_kWh'].sum().reset_index()

    fig_forecast = go.Figure()

    fig_forecast.add_trace(go.Scatter(
        x=hist_2024['Month'], y=hist_2024['Consumption_kWh'],
        name='2024 فعلي', mode='lines',
        line=dict(color='#58a6ff', width=1.5, dash='dot'),
        opacity=0.6,
        hovertemplate='2024 | الشهر %{x}: %{y:,.0f}<extra></extra>'
    ))

    fig_forecast.add_trace(go.Scatter(
        x=hist_2025['Month'], y=hist_2025['Consumption_kWh'],
        name='2025 فعلي', mode='lines',
        line=dict(color='#3fb950', width=1.5, dash='dot'),
        opacity=0.6,
        hovertemplate='2025 | الشهر %{x}: %{y:,.0f}<extra></extra>'
    ))

    if len(actual_part) > 0:
        fig_forecast.add_trace(go.Scatter(
            x=actual_part['Month'], y=actual_part['Predicted_Consumption'],
            name='2026 فعلي', mode='lines+markers',
            line=dict(color='#f85149', width=3),
            marker=dict(size=8, color='#f85149', symbol='circle'),
            hovertemplate='2026 فعلي | الشهر %{x}: %{y:,.0f}<extra></extra>'
        ))

    if len(pred_part) > 0:
        r, g, b = 248, 81, 73
        fig_forecast.add_trace(go.Scatter(
            x=pred_part['Month'], y=pred_part['Predicted_Consumption'],
            name='2026 متوقع', mode='lines+markers',
            line=dict(color='#f85149', width=3, dash='dash'),
            marker=dict(size=8, color='#f85149', symbol='diamond'),
            fill='tozeroy',
            fillcolor=f'rgba({r},{g},{b},0.06)',
            hovertemplate='2026 متوقع | الشهر %{x}: %{y:,.0f}<extra></extra>'
        ))

    fig_forecast.update_layout(**dark_layout(height=380, showlegend=True))
    fig_forecast.update_layout(hovermode='x unified')
    fig_forecast.update_xaxes(**dark_xaxis(
        tickmode='array', tickvals=list(range(1, 13)),
        ticktext=[MONTH_NAMES[i] for i in range(1, 13)]
    ))
    fig_forecast.update_yaxes(**dark_yaxis(tickformat=',.0f'))
    st.plotly_chart(fig_forecast, use_container_width=True, key="forecast_main")

    st.markdown('<div class="section-header"><span class="section-icon">مقارنة</span><h3>مقارنة Q1 2026: الفعلي مقابل المتوقع</h3></div>', unsafe_allow_html=True)

    col_q1, col_q1_err = st.columns(2)

    with col_q1:
        fig_q1 = go.Figure()
        fig_q1.add_trace(go.Bar(
            x=[MONTH_NAMES[m] for m in q1_comp['Month']],
            y=q1_comp['فعلي'],
            name='فعلي',
            marker=dict(color='#3fb950', opacity=0.85)
        ))
        fig_q1.add_trace(go.Bar(
            x=[MONTH_NAMES[m] for m in q1_comp['Month']],
            y=q1_comp['متوقع'],
            name='متوقع',
            marker=dict(color='#f85149', opacity=0.85)
        ))
        fig_q1.update_layout(**dark_layout(height=280, showlegend=True))
        fig_q1.update_layout(barmode='group')
        fig_q1.update_xaxes(**dark_xaxis())
        fig_q1.update_yaxes(**dark_yaxis(tickformat=',.0f'))
        st.plotly_chart(fig_q1, use_container_width=True, key="q1_comp")

    with col_q1_err:
        q1_comp['خطأ_%'] = (q1_comp['متوقع'] - q1_comp['فعلي']) / q1_comp['فعلي'] * 100
        err_colors = ['#3fb950' if abs(e) < 10 else '#d29922' if abs(e) < 20 else '#f85149' for e in q1_comp['خطأ_%']]

        fig_err = go.Figure(go.Bar(
            x=[MONTH_NAMES[m] for m in q1_comp['Month']],
            y=q1_comp['خطأ_%'],
            marker=dict(color=err_colors, line=dict(color='#0d1117', width=1)),
            text=[f'{e:+.1f}%' for e in q1_comp['خطأ_%']],
            textposition='outside',
            textfont=dict(color='#8b949e', size=11)
        ))
        fig_err.add_hline(y=0, line_color='#484f58', line_width=1)
        fig_err.update_layout(**dark_layout(height=280, title='نسبة الخطأ في التنبؤ (%)', showlegend=False))
        fig_err.update_xaxes(**dark_xaxis())
        fig_err.update_yaxes(**dark_yaxis(ticksuffix='%'))
        st.plotly_chart(fig_err, use_container_width=True, key="q1_err")

    st.markdown('<div class="section-header"><span class="section-icon">أرباع</span><h3>توقعات الأرباع 2026</h3></div>', unsafe_allow_html=True)

    quarter_map = {1: 'Q1', 2: 'Q1', 3: 'Q1', 4: 'Q2', 5: 'Q2', 6: 'Q2',
                   7: 'Q3', 8: 'Q3', 9: 'Q3', 10: 'Q4', 11: 'Q4', 12: 'Q4'}
    quarter_colors = {'Q1': '#3fb950', 'Q2': '#58a6ff', 'Q3': '#f85149', 'Q4': '#d29922'}

    pred_df_copy = pred_df.copy()
    pred_df_copy['Quarter'] = pred_df_copy['Month'].map(quarter_map)
    q_summary = pred_df_copy.groupby(['Quarter', 'Type'])['Predicted_Consumption'].sum().reset_index()

    q_cols = st.columns(4)
    for i, q in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
        q_data = q_summary[q_summary['Quarter'] == q]
        q_total = q_data['Predicted_Consumption'].sum()
        q_type = q_data['Type'].iloc[0] if len(q_data) > 0 else 'متوقع'
        q_label = {'Q1': 'الربع الأول', 'Q2': 'الربع الثاني', 'Q3': 'الربع الثالث', 'Q4': 'الربع الرابع'}[q]
        q_color = quarter_colors[q]
        with q_cols[i]:
            st.markdown(f"""
            <div class="quarter-card">
                <h4>{q_label}</h4>
                <div class="q-value" style="color:{q_color};">{fmt_num(q_total)}</div>
                <div class="q-label">كيلوواط/ساعة</div>
                <div style="margin-top:8px;">
                    <span class="badge" style="background:{q_color}22; color:{q_color}; border:1px solid {q_color}44;">
                        {'فعلي' if q_type == 'فعلي' else 'متوقع'}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    q_chart_cols = st.columns(2)

    for idx, (q, q_color) in enumerate([('Q2', '#58a6ff'), ('Q3', '#f85149')]):
        q_months = [m for m, qtr in quarter_map.items() if qtr == q]
        q_monthly = pred_df_copy[pred_df_copy['Month'].isin(q_months)].groupby('Month')['Predicted_Consumption'].sum().reset_index()
        q_monthly['Month_Name'] = q_monthly['Month'].map(MONTH_NAMES)

        r_c, g_c, b_c = int(q_color[1:3], 16), int(q_color[3:5], 16), int(q_color[5:7], 16)

        fig_q = go.Figure(go.Scatter(
            x=q_monthly['Month_Name'], y=q_monthly['Predicted_Consumption'],
            name='2026 متوقع', mode='lines+markers',
            line=dict(color=q_color, width=3),
            marker=dict(size=9, symbol='diamond'),
            fill='tozeroy',
            fillcolor=f'rgba({r_c},{g_c},{b_c},0.08)'
        ))
        q_label = {'Q2': 'الربع الثاني', 'Q3': 'الربع الثالث'}[q]
        fig_q.update_layout(**dark_layout(height=280, title=f'توقعات {q_label} 2026', showlegend=False))
        fig_q.update_xaxes(**dark_xaxis())
        fig_q.update_yaxes(**dark_yaxis(tickformat=',.0f'))

        with q_chart_cols[idx]:
            st.plotly_chart(fig_q, use_container_width=True, key=f"q{idx+2}_chart")

    st.markdown('<div class="section-header"><span class="section-icon">ملخص</span><h3>ملخص التوقعات السنوية</h3></div>', unsafe_allow_html=True)

    summary_data = {
        'السنة': ['2024 (فعلي)', '2025 (فعلي)', '2026 (متوقع)'],
        'الاستهلاك الكلي (كيلوواط)': [
            df[df['Year'] == 2024]['Consumption_kWh'].sum(),
            df[df['Year'] == 2025]['Consumption_kWh'].sum(),
            total_2026
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df['التغيير'] = summary_df['الاستهلاك الكلي (كيلوواط)'].pct_change() * 100

    fig_summary = go.Figure(go.Bar(
        x=summary_df['السنة'],
        y=summary_df['الاستهلاك الكلي (كيلوواط)'],
        marker=dict(
            color=['#58a6ff', '#3fb950', '#f85149'],
            line=dict(color='#0d1117', width=2)
        ),
        text=[fmt_num(v) for v in summary_df['الاستهلاك الكلي (كيلوواط)']],
        textposition='outside',
        textfont=dict(color='#e6edf3', size=13, family='Arial'),
        hovertemplate='%{x}<br>%{y:,.0f} كيلوواط<extra></extra>'
    ))
    fig_summary.update_layout(**dark_layout(height=300, showlegend=False))
    fig_summary.update_xaxes(**dark_xaxis())
    fig_summary.update_yaxes(**dark_yaxis(tickformat=',.0f'))
    st.plotly_chart(fig_summary, use_container_width=True, key="summary_bar")

# Footer
st.markdown("""
<div class="footer">
    لوحة تحليل استهلاك الكهرباء | هيئة الهلال الأحمر السعودي | الإصدار 2.0 | أبريل 2026
</div>
""", unsafe_allow_html=True)
