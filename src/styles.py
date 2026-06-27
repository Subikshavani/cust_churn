CSS = """
/* ════════════════════════════════════════════════════════
   DARK THEME — all values hardcoded, never falls back
   ════════════════════════════════════════════════════════ */

/* ── Font ── */
html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  color: #e5eefb !important;
  background-color: #07111f !important;
}

/* ── App background ── */
.stApp {
  background:
    radial-gradient(circle at top left, rgba(96,165,250,0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(110,231,255,0.12), transparent 28%),
    linear-gradient(180deg, #07111f 0%, #081425 45%, #060b14 100%) !important;
  color: #e5eefb !important;
}

/* ── Force light text on EVERY Streamlit element in dark mode ── */
.stApp *,
.stMarkdown, .stMarkdown *,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] *,
[data-testid="stText"],
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"],
.stCaption,
.stRadio label, .stSelectbox label,
.stSlider label, .stToggle label,
.stCheckbox label,
p, span, h1, h2, h3, h4, h5, h6, label, li, a {
  color: #e5eefb !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(5,12,24,0.97), rgba(10,18,34,0.95)) !important;
  border-right: 1px solid rgba(148,163,184,0.12) !important;
}
[data-testid="stSidebar"] * {
  color: #e5eefb !important;
}

/* ── Layout ── */
.block-container {
  padding-top: 4.5rem !important;
  padding-bottom: 2rem !important;
}

/* ── Glass card ── */
.glass-card {
  background: rgba(14,24,40,0.82) !important;
  border: 1px solid rgba(148,163,184,0.18) !important;
  border-radius: 22px !important;
  padding: 1.1rem 1.2rem !important;
  box-shadow: 0 24px 80px rgba(0,0,0,0.3) !important;
  backdrop-filter: blur(18px) !important;
  color: #e5eefb !important;
}
.glass-card * { color: #e5eefb !important; }

/* ── KPI card ── */
.kpi-card {
  background: linear-gradient(145deg, rgba(16,26,44,0.94), rgba(10,18,34,0.82)) !important;
  border: 1px solid rgba(148,163,184,0.16) !important;
  border-radius: 20px !important;
  padding: 1rem 1.1rem !important;
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease !important;
  color: #e5eefb !important;
}
.kpi-card * { color: #e5eefb !important; }
.kpi-card:hover {
  transform: translateY(-3px);
  border-color: rgba(110,231,255,0.28) !important;
  box-shadow: 0 18px 40px rgba(0,0,0,0.28) !important;
}

/* ── KPI text ── */
.kpi-value {
  font-size: 2rem !important;
  font-weight: 800 !important;
  line-height: 1.1 !important;
  color: #f8fbff !important;
}
.kpi-label {
  font-size: 0.82rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.14em !important;
  color: #9fb2c9 !important;
}

/* ── Form ── */
[data-testid="stForm"] {
  background: rgba(13,22,36,0.65) !important;
  border: 1px solid rgba(148,163,184,0.15) !important;
  border-radius: 22px !important;
  padding: 1rem !important;
  color: #e5eefb !important;
}
[data-testid="stForm"] * { color: #e5eefb !important; }

/* ── Input / select boxes in dark mode ── */
[data-baseweb="input"] input,
[data-baseweb="select"] div,
[data-baseweb="textarea"] textarea {
  background: rgba(14,24,40,0.9) !important;
  color: #e5eefb !important;
  border-color: rgba(148,163,184,0.25) !important;
}

/* ── Sidebar brand ── */
.sidebar-brand-title {
  font-size: 1.35rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.02em !important;
  color: #6ee7ff !important;
  margin-bottom: 0.2rem !important;
}
.sidebar-brand-subtitle {
  color: #92a5bf !important;
  font-size: 0.82rem !important;
  line-height: 1.3 !important;
}

/* ── Page headings ── */
.brand-title {
  font-size: 2.2rem !important;
  font-weight: 800 !important;
  line-height: 1.2 !important;
  color: #f8fbff !important;
  margin-bottom: 0.3rem !important;
}
.brand-subtitle {
  color: #92a5bf !important;
  font-size: 1.05rem !important;
  margin-bottom: 1.5rem !important;
}
.section-title {
  font-size: 1.15rem !important;
  font-weight: 700 !important;
  margin-bottom: 0.75rem !important;
  color: #e5eefb !important;
}

/* ── Badges ── */
.badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 0.4rem !important;
  border-radius: 999px !important;
  padding: 0.45rem 0.8rem !important;
  font-weight: 700 !important;
  font-size: 0.82rem !important;
}
.badge-low    { background: rgba(52,211,153,0.14) !important; color: #34d399 !important; }
.badge-medium { background: rgba(245,158,11,0.14) !important; color: #f59e0b !important; }
.badge-high   { background: rgba(248,113,113,0.14) !important; color: #f87171 !important; }

/* ── DataFrames / Tables in dark mode ── */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] td {
  color: #e5eefb !important;
  background: rgba(14,24,40,0.85) !important;
  border-color: rgba(148,163,184,0.15) !important;
}

/* ── Charts / Plotly in dark mode ── */
.js-plotly-plot .plotly text,
.js-plotly-plot .plotly .xtitle,
.js-plotly-plot .plotly .ytitle,
.js-plotly-plot .plotly .gtitle,
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text {
  fill: #e5eefb !important;
  color: #e5eefb !important;
}
.js-plotly-plot .plotly .legend rect.bg {
  fill: rgba(10,18,34,0.92) !important;
  stroke: rgba(110,231,255,0.3) !important;
}
.js-plotly-plot .plotly .legend text {
  fill: #e5eefb !important;
}
.js-plotly-plot .plotly .gridlayer path,
.js-plotly-plot .plotly .zerolinelayer path {
  stroke: rgba(148,163,184,0.12) !important;
}

/* ── Primary button ── */
button[kind="primary"] {
  background: linear-gradient(90deg, #6ee7ff, #60a5fa) !important;
  color: #07111f !important;
  font-weight: 800 !important;
  border-radius: 14px !important;
  border: none !important;
}
"""
