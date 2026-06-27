CSS = """
/* ── Dark theme hardcoded — never falls back to browser defaults ── */

:root {
  --panel: rgba(14, 24, 40, 0.82);
  --panel-border: rgba(148, 163, 184, 0.18);
  --accent: #6ee7ff;
  --accent-2: #60a5fa;
  --success: #34d399;
  --warning: #f59e0b;
  --danger: #f87171;
}

html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #e5eefb !important;
  background-color: #07111f !important;
}

/* ── App shell ── */
.stApp {
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(110, 231, 255, 0.12), transparent 28%),
    linear-gradient(180deg, #07111f 0%, #081425 45%, #060b14 100%) !important;
  color: #e5eefb !important;
}

/* ── Force white text on ALL Streamlit text nodes ── */
.stApp p, .stApp span, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp label, .stApp li, .stApp a,
.stMarkdown, .stMarkdown p, .stMarkdown span,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown li,
[data-testid="stText"], [data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] *,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stMetricDelta"],
.stCaption, .stRadio label, .stSelectbox label,
.stSlider label, .stToggle label, .stCheckbox label {
  color: #e5eefb !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(5, 12, 24, 0.97), rgba(10, 18, 34, 0.95)) !important;
  border-right: 1px solid rgba(148, 163, 184, 0.12) !important;
}
[data-testid="stSidebar"] * {
  color: #e5eefb !important;
}

/* ── Layout ── */
.block-container {
  padding-top: 4.5rem !important;
  padding-bottom: 2rem;
}

/* ── Glass card ── */
.glass-card {
  background: rgba(14, 24, 40, 0.82) !important;
  border: 1px solid rgba(148, 163, 184, 0.18) !important;
  border-radius: 22px;
  padding: 1.1rem 1.2rem;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(18px);
}

/* ── KPI card ── */
.kpi-card {
  background: linear-gradient(145deg, rgba(16, 26, 44, 0.94), rgba(10, 18, 34, 0.82)) !important;
  border: 1px solid rgba(148, 163, 184, 0.16) !important;
  border-radius: 20px;
  padding: 1rem 1.1rem;
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}
.kpi-card:hover {
  transform: translateY(-3px);
  border-color: rgba(110, 231, 255, 0.28) !important;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
}

/* ── KPI text ── */
.kpi-value {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1.1;
  color: #f8fbff !important;
}
.kpi-label {
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: #9fb2c9 !important;
}

/* ── Sidebar brand ── */
.sidebar-brand-title {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: #6ee7ff !important;
  margin-bottom: 0.2rem;
}
.sidebar-brand-subtitle {
  color: #92a5bf !important;
  font-size: 0.82rem;
  line-height: 1.3;
}

/* ── Page headings ── */
.brand-title {
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1.2;
  color: #f8fbff !important;
  margin-bottom: 0.3rem;
}
.brand-subtitle {
  color: #92a5bf !important;
  font-size: 1.05rem;
  margin-bottom: 1.5rem;
}
.section-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: #e5eefb !important;
}

/* ── Badges ── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  font-weight: 700;
  font-size: 0.82rem;
}
.badge-low    { background: rgba(52, 211, 153, 0.14); color: #34d399 !important; }
.badge-medium { background: rgba(245, 158, 11, 0.14);  color: #f59e0b !important; }
.badge-high   { background: rgba(248, 113, 113, 0.14); color: #f87171 !important; }

/* ── Form ── */
[data-testid="stForm"] {
  background: rgba(13, 22, 36, 0.65) !important;
  border: 1px solid rgba(148, 163, 184, 0.15) !important;
  border-radius: 22px;
  padding: 1rem;
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
