"""
figures.py — Generate report figures (charts and diagrams) with matplotlib.

Charts (risk distribution, top risks) are built from a real assessment run on
the seeded demo data. Diagrams (architecture, data-flow, threat model) are drawn
programmatically so they regenerate deterministically.
"""

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend for file output
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# Make backend modules importable
_BACKEND = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

CRIT_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#CA8A04",
    "Low": "#16A34A",
}


def _build_register():
    """Seed demo data and return a real risk register."""
    import seed_data
    from database import models
    from modules.risk_engine import build_risk_register

    seed_data.seed("report-demo", reset=True)
    assets = models.get_assets_with_threats("report-demo")
    return build_risk_register(assets)


def fig_risk_distribution(register) -> str:
    """Pie chart of risk count by criticality. Returns file path."""
    counts: dict[str, int] = {}
    for r in register:
        c = r["risk_criticality"]
        counts[c] = counts.get(c, 0) + 1
    order = [c for c in ["Critical", "High", "Medium", "Low"] if c in counts]
    sizes = [counts[c] for c in order]
    colors = [CRIT_COLORS[c] for c in order]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(sizes, labels=order, colors=colors, autopct="%1.0f%%", startangle=90)
    ax.axis("equal")
    ax.set_title("Risk Distribution by Criticality")
    path = FIG_DIR / "risk_distribution.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def fig_top_risks(register) -> str:
    """Horizontal bar chart of top risks by impact rating. Returns file path."""
    top = register[:8]
    labels = [f"{r['asset_name'][:18]}\n{r['threat_name'][:18]}" for r in top][::-1]
    values = [r["risk_impact_rating"] for r in top][::-1]
    colors = [CRIT_COLORS[r["risk_criticality"]] for r in top][::-1]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(labels, values, color=colors)
    ax.set_xlabel("Risk Impact Rating (AssessITS, 1-250)")
    ax.set_title("Top Risks by Impact Rating")
    ax.set_xlim(0, 250)
    fig.tight_layout()
    path = FIG_DIR / "top_risks.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def fig_ale_by_asset(register) -> str:
    """Bar chart of total ALE per asset. Returns file path."""
    ale_by_asset: dict[str, float] = {}
    for r in register:
        ale_by_asset[r["asset_name"]] = ale_by_asset.get(r["asset_name"], 0) + r["ale"]
    names = list(ale_by_asset.keys())
    short = [n[:16] for n in names]
    values = [ale_by_asset[n] for n in names]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(short, values, color="#2563eb")
    ax.set_ylabel("Annualised Loss Expectancy (USD)")
    ax.set_title("Total ALE by Asset")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=8)
    fig.tight_layout()
    path = FIG_DIR / "ale_by_asset.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def _box(ax, x, y, w, h, text, fc="#dbeafe", ec="#1e3a5f"):
    """Draw a labelled rounded rectangle."""
    box = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        fc=fc, ec=ec, lw=1.5,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, wrap=True)


def _arrow(ax, x1, y1, x2, y2):
    """Draw an arrow between two points."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="#475569", lw=1.4))


def fig_architecture() -> str:
    """System architecture block diagram. Returns file path."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    _box(ax, 0.5, 5.2, 2.4, 1.2, "React Frontend\n(Vite + Tailwind\n+ Recharts)", fc="#e0f2fe")
    _box(ax, 4.0, 5.2, 2.4, 1.2, "Flask REST API\n(JSON envelope\n+ rate limiting)", fc="#dbeafe")
    _box(ax, 7.4, 5.2, 2.1, 1.2, "SQLite DB\n(parameterised)", fc="#dcfce7")

    _box(ax, 3.6, 3.2, 1.5, 1.0, "Risk Engine\nSLE/ALE/R", fc="#fef9c3")
    _box(ax, 5.3, 3.2, 1.5, 1.0, "Report Gen\n(ReportLab)", fc="#fef9c3")
    _box(ax, 1.9, 3.2, 1.5, 1.0, "CVE Fetcher\n(NVD)", fc="#fde68a")
    _box(ax, 7.0, 3.2, 1.5, 1.0, "LLM Advisor\n(Claude)", fc="#fde68a")

    _box(ax, 1.9, 1.2, 1.5, 0.9, "NVD API\n(+ mock)", fc="#fee2e2")
    _box(ax, 7.0, 1.2, 1.5, 0.9, "Claude API\n(+ fallback)", fc="#fee2e2")

    _arrow(ax, 2.9, 5.8, 4.0, 5.8)
    _arrow(ax, 6.4, 5.8, 7.4, 5.8)
    _arrow(ax, 5.2, 5.2, 4.6, 4.2)
    _arrow(ax, 5.2, 5.2, 6.0, 4.2)
    _arrow(ax, 4.6, 5.2, 2.9, 4.2)
    _arrow(ax, 5.6, 5.2, 7.5, 4.2)
    _arrow(ax, 2.65, 3.2, 2.65, 2.1)
    _arrow(ax, 7.75, 3.2, 7.75, 2.1)

    ax.set_title("Figure: System Architecture", fontsize=11)
    path = FIG_DIR / "architecture.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def fig_dataflow() -> str:
    """Data-flow diagram. Returns file path."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis("off")

    steps = [
        ("User\nInput", "#e0f2fe"),
        ("Validate\n+ Escape", "#dbeafe"),
        ("Store\n(SQLite)", "#dcfce7"),
        ("Risk\nEngine", "#fef9c3"),
        ("LLM +\nCVE", "#fde68a"),
        ("Report\n/ PDF", "#fee2e2"),
    ]
    x = 0.3
    centers = []
    for text, fc in steps:
        _box(ax, x, 1.0, 1.6, 1.0, text, fc=fc)
        centers.append(x + 1.6)
        x += 2.0
    for i in range(len(steps) - 1):
        _arrow(ax, centers[i], 1.5, centers[i] + 0.4, 1.5)

    ax.set_title("Figure: Data-Flow Diagram", fontsize=11)
    path = FIG_DIR / "dataflow.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def fig_threat_model() -> str:
    """STRIDE-style threat model diagram. Returns file path."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    stride = [
        ("Spoofing", "Session id validation"),
        ("Tampering", "Parameterised queries"),
        ("Repudiation", "Assessment audit records"),
        ("Info Disclosure", "Output HTML escaping"),
        ("Denial of Service", "Rate limiting 100/min"),
        ("Elevation of Priv.", "Session-scoped data"),
    ]
    y = 6.8
    for threat, control in stride:
        _box(ax, 0.5, y, 3.5, 0.9, threat, fc="#fee2e2")
        _box(ax, 5.0, y, 4.3, 0.9, control, fc="#dcfce7")
        _arrow(ax, 4.0, y + 0.45, 5.0, y + 0.45)
        y -= 1.1

    ax.text(2.25, 7.9, "Threat (STRIDE)", ha="center", fontsize=10, weight="bold")
    ax.text(7.15, 7.9, "Mitigating Control", ha="center", fontsize=10, weight="bold")
    ax.set_title("Figure: Threat Model (STRIDE mapping)", fontsize=11)
    path = FIG_DIR / "threat_model.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def generate_all():
    """Generate every figure and return a dict of name -> path plus the register."""
    register = _build_register()
    return {
        "register": register,
        "risk_distribution": fig_risk_distribution(register),
        "top_risks": fig_top_risks(register),
        "ale_by_asset": fig_ale_by_asset(register),
        "architecture": fig_architecture(),
        "dataflow": fig_dataflow(),
        "threat_model": fig_threat_model(),
    }


if __name__ == "__main__":
    out = generate_all()
    print(f"Generated {len([k for k in out if k != 'register'])} figures in {FIG_DIR}")
