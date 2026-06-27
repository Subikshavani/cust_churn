"""Export & Reporting utilities for the Telco Churn Intelligence Platform.

Provides:
  - generate_pdf_report  : branded 4-page PDF with KPIs, charts, high-risk table
  - generate_customer_csv: full scored customer table as UTF-8 CSV bytes
  - send_email_alert     : SMTP digest of high-risk customers
"""

from __future__ import annotations

import datetime
import io
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# ─── optional dependency guards ───────────────────────────────────────────────
try:
    from fpdf import FPDF, XPos, YPos  # fpdf2 >= 2.7
    _FPDF_OK = True
except ImportError:  # pragma: no cover
    _FPDF_OK = False
    FPDF = object
    XPos = object
    YPos = object

try:
    import plotly.io as _pio
    _KALEIDO_OK = True
except ImportError:  # pragma: no cover
    _KALEIDO_OK = False


# ─── brand palette (RGB tuples matching the UI) ───────────────────────────────
_BG_DARK = (18,  22,  36)
_BG_MID  = (28,  33,  55)
_BG_CARD = (40,  47,  72)
_TEAL    = (52,  211, 153)
_CYAN    = (110, 231, 255)
_AMBER   = (251, 191,  36)
_RED     = (248, 113, 113)
_WHITE   = (255, 255, 255)
_LIGHT   = (200, 215, 235)
_MUTED   = (110, 125, 160)


# ─────────────────────────────────────────────────────────────────────────────
# Internal PDF class
# ─────────────────────────────────────────────────────────────────────────────

class _ChurnPDF(FPDF):
    """FPDF subclass with brand-styled helpers."""

    def full_bg(self) -> None:
        """Fill entire page with dark background."""
        self.set_fill_color(*_BG_DARK)
        self.rect(0, 0, self.w, self.h, "F")

    def accent_bar(self, y: float = 0, h: float = 4) -> None:
        """Draw a teal horizontal bar spanning the full page width."""
        self.set_fill_color(*_TEAL)
        self.rect(0, y, self.w, h, "F")

    def section_header(self, title: str) -> None:
        """Render a cyan section header with a separator line."""
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*_CYAN)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        cur_y = self.get_y()
        self.set_draw_color(*_CYAN)
        self.set_line_width(0.4)
        self.line(10, cur_y, self.w - 10, cur_y)
        self.ln(4)

    def kpi_box(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        label: str,
        value: str,
        color: tuple = _TEAL,
    ) -> None:
        """Draw a single branded KPI card."""
        # Card background
        self.set_fill_color(*_BG_CARD)
        self.rect(x, y, w, h, "F")
        # Left accent stripe
        self.set_fill_color(*color)
        self.rect(x, y, 3, h, "F")
        # Label
        self.set_xy(x + 5, y + 3)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*_MUTED)
        self.cell(w - 8, 5, label.upper())
        # Value
        self.set_xy(x + 5, y + 10)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*_WHITE)
        self.cell(w - 8, 9, value)

    def footer_bar(self, text: str = "CONFIDENTIAL — Telco Churn Intelligence Platform") -> None:
        """Draw branded footer."""
        self.accent_bar(y=self.h - 5, h=5)
        self.set_xy(10, self.h - 12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*_MUTED)
        self.cell(0, 6, text, align="C")


# ─────────────────────────────────────────────────────────────────────────────
# Chart-to-PNG helper
# ─────────────────────────────────────────────────────────────────────────────

def _plotly_to_png(fig, width: int = 760, height: int = 300) -> Optional[bytes]:
    """Export a Plotly figure to PNG bytes via kaleido. Returns None on failure."""
    if not _KALEIDO_OK:
        return None
    try:
        return _pio.to_image(fig, format="png", width=width, height=height, scale=2)
    except Exception:
        return None


def _matplotlib_charts_png(df: pd.DataFrame) -> Optional[bytes]:
    """Fallback: render risk distribution + revenue impact via matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        colors_map = {
            "High Risk":   "#f87171",
            "Medium Risk": "#fbbf24",
            "Low Risk":    "#34d399",
        }

        fig, axes = plt.subplots(1, 2, figsize=(13, 4))
        fig.patch.set_facecolor("#121624")

        # Risk distribution
        risk_counts = df["risk_category"].value_counts()
        bar_colors = [colors_map.get(str(r), "#6ee7ff") for r in risk_counts.index]
        ax1 = axes[0]
        ax1.set_facecolor("#1c2137")
        ax1.bar(risk_counts.index, risk_counts.values, color=bar_colors, edgecolor="none")
        ax1.set_title("Customer Risk Distribution", color="#6ee7ff", fontsize=12, pad=8)
        ax1.tick_params(colors="#c8d7eb", labelsize=9)
        ax1.set_ylabel("Customers", color="#c8d7eb", fontsize=9)
        for spine in ax1.spines.values():
            spine.set_color("#283668")

        # Monthly revenue by risk
        rev_grouped = df.groupby("risk_category", observed=True)["MonthlyCharges"].sum()
        rev_colors = [colors_map.get(str(r), "#6ee7ff") for r in rev_grouped.index]
        ax2 = axes[1]
        ax2.set_facecolor("#1c2137")
        ax2.bar(rev_grouped.index, rev_grouped.values, color=rev_colors, edgecolor="none")
        ax2.set_title("Monthly Revenue by Risk", color="#6ee7ff", fontsize=12, pad=8)
        ax2.tick_params(colors="#c8d7eb", labelsize=9)
        ax2.set_ylabel("Monthly Charges ($)", color="#c8d7eb", fontsize=9)
        for spine in ax2.spines.values():
            spine.set_color("#283668")

        plt.tight_layout(pad=2)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf_report(df: pd.DataFrame, metrics: Dict[str, Any]) -> bytes:
    """Build a branded 4-page PDF executive report.

    Pages:
      1. Cover with 8 KPI cards
      2. Full KPI table + model performance comparison
      3. Visual analytics (charts)
      4. Top-20 high-risk customers table

    Returns PDF as raw bytes for use with st.download_button.
    Raises RuntimeError if fpdf2 is not installed.
    """
    if not _FPDF_OK:
        raise RuntimeError(
            "fpdf2 is not installed. Run:  pip install fpdf2"
        )

    now        = datetime.datetime.now()
    best_model = metrics.get("best_model", "LightGBM")

    total        = len(df)
    churned      = int((df["ChurnBinary"] == 1).sum())
    active       = total - churned
    churn_rate   = churned / max(total, 1)
    high_risk_df = df[df["risk_category"] == "High Risk"]
    high_risk_n  = len(high_risk_df)
    monthly_risk = float(high_risk_df["MonthlyCharges"].sum())
    annual_risk  = monthly_risk * 12
    avg_clv      = float((df["MonthlyCharges"] * df["tenure"]).mean())
    avg_health   = float(df["health_score"].mean())

    pdf = _ChurnPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(10, 10, 10)

    # ── PAGE 1: Cover ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.full_bg()
    pdf.accent_bar(y=0, h=5)

    pdf.set_y(28)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*_TEAL)
    pdf.cell(0, 13, "TELCO CHURN INTELLIGENCE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(*_LIGHT)
    pdf.cell(0, 9, "Executive Performance Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.ln(6)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_MUTED)
    pdf.cell(0, 5, f"Generated:  {now.strftime('%d %B %Y   %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, f"Active Model:  {best_model}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # Divider
    pdf.ln(6)
    pdf.set_draw_color(*_BG_CARD)
    pdf.set_line_width(0.4)
    pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
    pdf.ln(4)

    # 8 KPI boxes in 2-column x 4-row grid
    kpis = [
        ("Total Customers",        f"{total:,}",             _CYAN),
        ("Churned Customers",      f"{churned:,}",           _RED),
        ("Churn Rate",             f"{churn_rate*100:.1f}%", _AMBER),
        ("High-Risk Count",        f"{high_risk_n:,}",       _RED),
        ("Monthly Revenue Risk",   f"${monthly_risk:,.0f}",  _AMBER),
        ("Annual Revenue Risk",    f"${annual_risk:,.0f}",   _RED),
        ("Avg Customer Lifetime",  f"${avg_clv:,.0f}",       _TEAL),
        ("Avg Health Index",       f"{avg_health:.1f}/100",  _TEAL),
    ]
    box_w, box_h, gap_x, gap_y = 88, 26, 4, 4
    start_y = pdf.get_y()
    for i, (label, value, color) in enumerate(kpis):
        col = i % 2
        row = i // 2
        bx  = 10 + col * (box_w + gap_x)
        by  = start_y + row * (box_h + gap_y)
        pdf.kpi_box(bx, by, box_w, box_h, label, value, color)

    pdf.footer_bar()

    # ── PAGE 2: KPI Table + Model Comparison ──────────────────────────────────
    pdf.add_page()
    pdf.full_bg()
    pdf.accent_bar(y=0, h=4)

    pdf.set_y(12)
    pdf.section_header("KPI SUMMARY")

    table_rows = [
        ("Total Customers",           f"{total:,}"),
        ("Active Customers",          f"{active:,}"),
        ("Churned Customers",         f"{churned:,}"),
        ("Churn Rate",                f"{churn_rate*100:.1f}%"),
        ("High-Risk Customers",       f"{high_risk_n:,}"),
        ("Monthly Revenue at Risk",   f"${monthly_risk:,.2f}"),
        ("Annual Revenue at Risk",    f"${annual_risk:,.2f}"),
        ("30% Retention Savings",     f"${annual_risk*0.3:,.2f}"),
        ("60% Retention Savings",     f"${annual_risk*0.6:,.2f}"),
        ("Avg Customer Lifetime Value", f"${avg_clv:,.2f}"),
        ("Avg Customer Health Index",   f"{avg_health:.1f} / 100"),
        ("Active ML Model",             best_model),
        ("Report Generated",            now.strftime("%d %B %Y  %H:%M")),
    ]

    row_h = 8
    for idx, (lbl, val) in enumerate(table_rows):
        fill_color = _BG_CARD if idx % 2 == 0 else _BG_MID
        pdf.set_fill_color(*fill_color)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*_LIGHT)
        pdf.cell(112, row_h, f"  {lbl}", fill=True)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*_WHITE)
        pdf.cell(78, row_h, val, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)
    pdf.section_header("MODEL PERFORMANCE METRICS")

    model_metrics: Dict[str, Dict[str, float]] = metrics.get("metrics", {})
    if model_metrics:
        col_widths = [58, 24, 25, 22, 20, 24]
        headers    = ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
        pdf.set_fill_color(*_BG_MID)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_CYAN)
        for cw, ch in zip(col_widths, headers):
            pdf.cell(cw, 7, ch, fill=True, align="C")
        pdf.ln()

        for i, (mname, m) in enumerate(model_metrics.items()):
            pdf.set_fill_color(*(_BG_CARD if i % 2 == 0 else _BG_MID))
            pdf.set_font("Helvetica", "B" if mname == best_model else "", 8)
            pdf.set_text_color(*_TEAL if mname == best_model else _LIGHT)
            row_vals = [
                mname + (" ★" if mname == best_model else ""),
                f"{m.get('accuracy', 0)*100:.1f}%",
                f"{m.get('precision', 0)*100:.1f}%",
                f"{m.get('recall', 0)*100:.1f}%",
                f"{m.get('f1', 0)*100:.1f}%",
                f"{m.get('roc_auc', 0):.4f}",
            ]
            for cw, rv in zip(col_widths, row_vals):
                pdf.cell(cw, 7, rv, fill=True, align="C")
            pdf.ln()

    pdf.footer_bar()

    # ── PAGE 3: Visual Analytics ──────────────────────────────────────────────
    pdf.add_page()
    pdf.full_bg()
    pdf.accent_bar(y=0, h=4)
    pdf.set_y(12)
    pdf.section_header("VISUAL ANALYTICS")

    charts_ok = False

    # Try kaleido first
    if _KALEIDO_OK:
        try:
            from .charts import risk_distribution, revenue_impact, kpi_timeline  # noqa: PLC0415

            cur_y = pdf.get_y()
            for chart_fn, title in [
                (risk_distribution, "Customer Risk Distribution"),
                (revenue_impact,    "Monthly Revenue by Risk Band"),
                (kpi_timeline,      "Churn Trend by Tenure"),
            ]:
                fig = chart_fn(df)
                img = _plotly_to_png(fig, width=760, height=280)
                if img:
                    pdf.image(io.BytesIO(img), x=10, y=pdf.get_y(), w=190, type="PNG")
                    pdf.ln(75)
                    charts_ok = True
        except Exception:
            charts_ok = False

    # Fallback: matplotlib
    if not charts_ok:
        img = _matplotlib_charts_png(df)
        if img:
            pdf.image(io.BytesIO(img), x=10, y=pdf.get_y(), w=190, type="PNG")
        else:
            pdf.set_text_color(*_MUTED)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(
                0, 10,
                "Install 'kaleido' (pip install kaleido) to embed interactive charts in PDF.",
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )

    pdf.footer_bar()

    # ── PAGE 4: Top High-Risk Customers ───────────────────────────────────────
    pdf.add_page()
    pdf.full_bg()
    pdf.accent_bar(y=0, h=4)
    pdf.set_y(12)

    top_n = min(high_risk_n, 20)
    pdf.section_header(f"TOP HIGH-RISK CUSTOMERS  ({top_n} of {high_risk_n})")

    top_risk = (
        df[df["risk_category"] == "High Risk"]
        .nlargest(20, "churn_probability")[
            ["gender", "Contract", "InternetService", "MonthlyCharges",
             "tenure", "churn_probability", "health_score", "Segment"]
        ]
        .reset_index(drop=True)
    )

    col_defs: List[Tuple[str, int, str]] = [
        ("#",          8,  "C"),
        ("Gender",    18,  "C"),
        ("Contract",  40,  "C"),
        ("Internet",  30,  "C"),
        ("$/mo",      22,  "C"),
        ("Tenure",    18,  "C"),
        ("Churn%",    22,  "C"),
        ("Health",    20,  "C"),
        ("Segment",   12,  "C"),
    ]

    # Header
    pdf.set_fill_color(*_BG_MID)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_CYAN)
    for hdr, cw, align in col_defs:
        pdf.cell(cw, 7, hdr, fill=True, align=align)
    pdf.ln()

    for i, row in top_risk.iterrows():
        pdf.set_fill_color(*(_BG_CARD if i % 2 == 0 else _BG_MID))
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*_LIGHT)
        vals = [
            str(i + 1),
            str(row["gender"]),
            str(row["Contract"]),
            str(row["InternetService"]),
            f"${row['MonthlyCharges']:.0f}",
            f"{int(row['tenure'])}mo",
            f"{row['churn_probability']*100:.1f}%",
            f"{row['health_score']:.0f}",
            str(row["Segment"])[:12],
        ]
        for (_, cw, align), v in zip(col_defs, vals):
            pdf.cell(cw, 6, v, fill=True, align=align)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*_MUTED)
    pdf.cell(
        0, 6,
        f"Report generated {now.strftime('%d %B %Y at %H:%M')}  |  {total:,} customers analysed.",
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )
    pdf.footer_bar("CONFIDENTIAL — Telco Churn Intelligence Platform | Internal Use Only")

    return bytes(pdf.output())


# ─────────────────────────────────────────────────────────────────────────────

def generate_customer_csv(df: pd.DataFrame) -> bytes:
    """Return the full scored customer table as UTF-8 CSV bytes.

    Includes churn probability (%), risk category, health score, segment, and
    all demographic and service features.
    """
    export_cols = [
        "gender", "SeniorCitizen", "Partner", "Dependents",
        "tenure", "PhoneService", "InternetService", "OnlineSecurity",
        "TechSupport", "StreamingTV", "Contract", "PaymentMethod",
        "MonthlyCharges", "TotalCharges", "AverageChargePerMonth",
        "ChurnLabel", "churn_probability", "risk_category",
        "health_score", "health_category", "Segment",
    ]
    available = [c for c in export_cols if c in df.columns]
    out = df[available].copy()
    out.index = range(1, len(out) + 1)
    out.index.name = "CustomerIndex"
    if "churn_probability" in out.columns:
        out["churn_probability"] = (out["churn_probability"] * 100).round(2)
        out = out.rename(columns={"churn_probability": "ChurnProbability_%"})
    return out.to_csv().encode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────

def send_email_alert(
    smtp_config: Dict[str, Any],
    df: pd.DataFrame,
) -> Tuple[bool, str]:
    """Send a plain-text churn alert email via SMTP.

    Args:
        smtp_config: dict with keys:
            host, port, sender, password, recipients (list[str]),
            use_tls (bool, default True), attach_csv (bool, default False)
        df: scored customer DataFrame (result of get_dashboard_data)

    Returns:
        (success: bool, message: str)
    """
    try:
        high_risk = (
            df[df["risk_category"] == "High Risk"]
            .nlargest(10, "churn_probability")[
                ["gender", "Contract", "MonthlyCharges", "tenure",
                 "churn_probability", "health_score", "Segment"]
            ]
            .reset_index(drop=True)
        )

        total        = len(df)
        n_high       = int((df["risk_category"] == "High Risk").sum())
        n_medium     = int((df["risk_category"] == "Medium Risk").sum())
        monthly_risk = float(df.loc[df["risk_category"] == "High Risk", "MonthlyCharges"].sum())
        annual_risk  = monthly_risk * 12
        avg_health   = float(df["health_score"].mean())
        now_str      = datetime.datetime.now().strftime("%d %B %Y  %H:%M")

        # ── Plain-text body ────────────────────────────────────────────────
        sep = "=" * 66
        lines = [
            sep,
            "  TELCO CHURN INTELLIGENCE — HIGH-RISK ALERT DIGEST",
            sep,
            f"  Generated       : {now_str}",
            f"  Customers Monitored : {total:,}",
            f"  High-Risk Detected  : {n_high:,}",
            f"  Medium-Risk         : {n_medium:,}",
            f"  Monthly Revenue Risk: ${monthly_risk:,.2f}",
            f"  Annual Exposure     : ${annual_risk:,.2f}",
            f"  Avg Health Index    : {avg_health:.1f}/100",
            "",
            "TOP 10 HIGH-RISK CUSTOMERS",
            "-" * 66,
            f"{'#':<4}{'Contract':<22}{'$/mo':>8}{'Tenure':>9}{'Churn%':>9}{'Health':>8}",
            "-" * 66,
        ]
        for i, row in high_risk.iterrows():
            lines.append(
                f"{i+1:<4}{str(row['Contract']):<22}"
                f"${row['MonthlyCharges']:>6.0f}"
                f"{int(row['tenure']):>7}mo"
                f"{row['churn_probability']*100:>8.1f}%"
                f"{row['health_score']:>8.0f}"
            )

        lines += [
            "",
            "-" * 66,
            "RECOMMENDED RETENTION ACTIONS",
            "  1. Offer 25% loyalty discount to top-risk customers",
            "  2. Promote 1-Year contract upgrades for month-to-month plans",
            "  3. Waive Tech Support fees for 6 months on Fiber Optic plans",
            "  4. Assign dedicated Account Care Specialist to top 5 churners",
            "",
            "  Dashboard: http://localhost:8501",
            sep,
            "  Automated alert from the Telco Churn Intelligence Platform.",
        ]
        body = "\n".join(lines)

        # ── Build MIME message ─────────────────────────────────────────────
        msg            = MIMEMultipart("mixed")
        msg["Subject"] = (
            f"\u26a0 Churn Alert \u2014 {n_high} High-Risk Customers Detected  |  {now_str}"
        )
        msg["From"] = smtp_config["sender"]
        msg["To"]   = ", ".join(smtp_config["recipients"])
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if smtp_config.get("attach_csv", False):
            csv_bytes  = generate_customer_csv(df)
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(csv_bytes)
            encoders.encode_base64(attachment)
            fname = f"churn_report_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
            attachment.add_header(
                "Content-Disposition", f'attachment; filename="{fname}"'
            )
            msg.attach(attachment)

        # ── Send ───────────────────────────────────────────────────────────
        host       = smtp_config["host"]
        port       = int(smtp_config.get("port", 587))
        sender     = smtp_config["sender"]
        password   = smtp_config["password"]
        recipients = smtp_config["recipients"]
        use_tls    = smtp_config.get("use_tls", True)

        if port == 465:
            import ssl  # noqa: PLC0415
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=ctx) as server:
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())
        else:
            with smtplib.SMTP(host, port) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())

        return True, f"Alert email sent successfully to: {', '.join(recipients)}"

    except Exception as exc:
        return False, f"Failed to send email: {exc}"
